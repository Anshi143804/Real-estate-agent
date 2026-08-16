import asyncio
import os
import sys
import uuid
from typing import Optional, Union

from loguru import logger

from pipecat.audio.vad.silero import SileroVADAnalyzer
from pipecat.pipeline.pipeline import Pipeline
from pipecat.pipeline.runner import PipelineRunner
from pipecat.pipeline.task import PipelineParams, PipelineTask
from pipecat.frames.frames import TTSSpeakFrame
from pipecat.transports.smallwebrtc.transport import SmallWebRTCTransport
from pipecat.transports.smallwebrtc.connection import SmallWebRTCConnection, IceServer
from pipecat.transports.base_transport import TransportParams

from pipecat.services.cartesia.tts import CartesiaTTSService
from pipecat.services.deepgram.stt import DeepgramSTTService
from pipecat.services.google.llm import GoogleLLMService

from pipecat.processors.aggregators.llm_context import LLMContext
from pipecat.processors.aggregators.llm_response_universal import (
    LLMContextAggregatorPair,
)

from app.services.logger import PipecatEventLogger
from app.services.event_bridge import EventBridgeObserver

from pipecat.flows import FlowManager

from app.config import config
from app.flows.buyer_flow import greeting_node
from app.flows.handlers import (
    proceed_to_requirements_handler,
    property_search_handler,
    property_details_handler,
    property_comparison_handler,
    schedule_viewing_handler,
    conversation_analysis_handler,
    finalize_conversation_handler,
)


HANDLERS = {
    "proceed_to_requirements_handler": proceed_to_requirements_handler,
    "property_search_handler": property_search_handler,
    "property_details_handler": property_details_handler,
    "property_comparison_handler": property_comparison_handler,
    "schedule_viewing_handler": schedule_viewing_handler,
    "conversation_analysis_handler": conversation_analysis_handler,
    "finalize_conversation_handler": finalize_conversation_handler,
}


async def run_bot(
    transport_or_webrtc_conn: Union[SmallWebRTCTransport, SmallWebRTCConnection, None] = None,
    session_id: str = None,
    runner_args: Optional[dict] = None,
):
    session_id = session_id or str(uuid.uuid4())
    logger.info(f"Initializing Voice Agent session: {session_id}")

    try:
        stt_service = DeepgramSTTService(
            api_key=config.DEEPGRAM_API_KEY, 
            model="nova-2-general"
        )
        
        llm_service = GoogleLLMService(
            api_key=config.GEMINI_API_KEY,
            settings=GoogleLLMService.Settings(model="gemini-2.5-flash"),
        )
        
        tts_service = CartesiaTTSService(
            api_key=config.CARTESIA_API_KEY,
            settings=CartesiaTTSService.Settings(voice=config.CARTESIA_VOICE_ID),
        )

        context = LLMContext()

        context_aggregator = LLMContextAggregatorPair(context)
        
        user_aggregator = context_aggregator.user()
        assistant_aggregator = context_aggregator.assistant()

        event_logger = PipecatEventLogger()

        # 4. Setup Transport
        if isinstance(transport_or_webrtc_conn, SmallWebRTCTransport):
            transport = transport_or_webrtc_conn
            conn = getattr(transport, "_webrtc_connection", None) or getattr(
                transport, "webrtc_connection", None
            )
        else:
            conn = (
                transport_or_webrtc_conn
                if isinstance(transport_or_webrtc_conn, SmallWebRTCConnection)
                else SmallWebRTCConnection(
                    ice_servers=[IceServer(urls=["stun:stun.l.google.com:19302"])]
                )
            )
            transport = SmallWebRTCTransport(
                webrtc_connection=conn,
                params=TransportParams(
                    audio_in_enabled=True,
                    audio_in_sample_rate=16000,
                    audio_out_enabled=True,
                    audio_out_sample_rate=24000,
                    vad_enabled=True,
                    vad_analyzer=SileroVADAnalyzer()
                ),
            )

        pipeline = Pipeline(
            [
        transport.input(),
        stt_service,
        user_aggregator,
        event_logger,
        llm_service,
        tts_service,
        transport.output(),
        assistant_aggregator,

            ]
        )

        event_bridge = EventBridgeObserver(connection=conn, session_id=session_id)

        task = PipelineTask(
            pipeline=pipeline,
            params=PipelineParams(
                allow_interruptions=True,
                enable_metrics=True,
            ),
            observers=[event_bridge],
        )

        flow_manager = FlowManager(
            worker=task,
            llm=llm_service,
            context_aggregator=context_aggregator,
            transport=transport,
        )

        for action_type, handler_func in HANDLERS.items():
            flow_manager.register_action(action_type, handler_func)

        # 7. Lifecycle Event Handlers
        from pipecat.frames.frames import TTSSpeakFrame

        @transport.event_handler("on_client_connected")
        async def on_client_connected(transport_obj, client):
            logger.info("⚡ [CLIENT CONNECTED]: Initializing Flow Manager & Greeting...")

            event_bridge.send_call_started()

            from app.db.database import SessionLocal
            from app.db.crud.conversation import conversation_repo
            import uuid as _uuid

            flow_manager.state["session_id"] = session_id
            db = SessionLocal()
            try:
                conversation_repo.create_session(db, id=_uuid.UUID(session_id), status="ACTIVE")
            except Exception as e:
                logger.warning(f"Could not create conversation_sessions row for {session_id}: {e}")
            finally:
                db.close()

            await flow_manager.initialize(greeting_node())
        @transport.event_handler("on_client_disconnected")
        async def on_client_disconnected(transport_obj, client):
            logger.warning(f"🔌 [WEBRTC DISCONNECTED]: Client {client}")
            event_bridge.send_call_ended()
            await asyncio.sleep(0.5)
            await task.cancel()

        runner = PipelineRunner()
        logger.info("🚀 Voice Agent Pipeline running...")
        await runner.run(task)

    finally:
        logger.info("🔒 Voice Agent session clean termination completed.")


if __name__ == "__main__":
    try:
        logger.info("🚀 Starting Pipecat Voice Agent...")
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("🛑 Voice Agent stopped by user.")
    except Exception as e:
        logger.exception(f"❌ Voice Agent crashed: {e}")
        sys.exit(1)