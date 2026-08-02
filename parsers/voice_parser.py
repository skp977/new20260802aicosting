"""
============================================================
FILE NAME
voice_parser.py

PURPOSE
Transcribe audio files into text.

NOTE
No offline speech-to-text library is installed yet
(e.g. speech_recognition / whisper). Returns a friendly
message so the pipeline still completes.

INPUT
Audio file path (wav, mp3, m4a)

OUTPUT
{"text": ..., "source": ..., "type": "voice"}

LAST UPDATED
2026-08-02
============================================================
"""


class VoiceParser:

    def parse(self, source):

        return {
            "text": (
                "[Voice transcription not available] No speech-to-text "
                "engine is installed. Install 'speech_recognition' with "
                "a backend (or OpenAI Whisper) and retry."
            ),
            "source": str(source),
            "type": "voice",
            "engine": "unavailable"
        }
