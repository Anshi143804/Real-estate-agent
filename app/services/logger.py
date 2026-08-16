from pipecat.frames.frames import (
    TextFrame,
    TranscriptionFrame,
    LLMFullResponseStartFrame,
    LLMFullResponseEndFrame,
    FunctionCallInProgressFrame,
    FunctionCallResultFrame,
    ErrorFrame,
)
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor
from loguru import logger


class PipecatEventLogger(FrameProcessor):
    """
    Intercepts pipeline frames to log:
    - User Transcripts (STT)
    - Bot Spoken Output (TTS/LLM)
    - Function/Tool Calls & Arguments
    - Function Execution Results
    - Pipeline Errors
    """

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        # 1. User STT Transcripts
        if isinstance(frame, TranscriptionFrame):
            logger.info(f"🗣️ [USER STT]: {frame.text}")

        # 2. Bot Text Tokens / Spoken Audio Content
        elif isinstance(frame, TextFrame) and direction == FrameDirection.DOWNSTREAM:
            logger.debug(f"🤖 [BOT CHUNK]: {frame.text}")

        # 3. LLM Full Response Markers
        elif isinstance(frame, LLMFullResponseStartFrame):
            logger.info("🤖 [BOT]: Started generating response...")

        # 4. Function / Tool Call Invocations
        elif isinstance(frame, FunctionCallInProgressFrame):
            logger.warning(
                f"🛠️ [FUNCTION CALL INITIATED]: Function='{frame.function_name}' | Arguments={frame.arguments}"
            )

        # 5. Function Execution Results
        elif isinstance(frame, FunctionCallResultFrame):
            logger.success(
                f"✅ [FUNCTION CALL RESULT]: Function='{frame.function_name}' | Result={frame.result}"
            )

        # 6. Pipeline Errors
        elif isinstance(frame, ErrorFrame):
            logger.error(f"❌ [PIPELINE ERROR]: {frame.error}")

        await self.push_frame(frame, direction)