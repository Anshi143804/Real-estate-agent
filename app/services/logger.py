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
    Intercepts pipeline frames to log user transcripts, bot output,
    function calls, results, and pipeline errors.
    """

    async def process_frame(self, frame, direction):
        await super().process_frame(frame, direction)

        if isinstance(frame, TranscriptionFrame):
            logger.info(f"🗣️ [USER STT]: {frame.text}")

        elif isinstance(frame, TextFrame) and direction == FrameDirection.DOWNSTREAM:
            logger.debug(f"🤖 [BOT CHUNK]: {frame.text}")

        elif isinstance(frame, LLMFullResponseStartFrame):
            logger.info("🤖 [BOT]: Started generating response...")

        elif isinstance(frame, FunctionCallInProgressFrame):
            logger.warning(
                f"🛠️ [FUNCTION CALL INITIATED]: Function='{frame.function_name}' | Arguments={frame.arguments}"
            )

        elif isinstance(frame, FunctionCallResultFrame):
            logger.success(
                f"✅ [FUNCTION CALL RESULT]: Function='{frame.function_name}' | Result={frame.result}"
            )

        elif isinstance(frame, ErrorFrame):
            logger.error(f"❌ [PIPELINE ERROR]: {frame.error}")

        await self.push_frame(frame, direction)