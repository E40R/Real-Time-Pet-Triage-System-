PawsPalConnect Assignment
Submitted by: M K Kiriti

<b>Pet Health Voice Agent - Modular Architecture </b>
A real-time voice consultation system for pet health using LangChain and Perplexity AI.


Note: This project avoids external third-party pipelines and relies only on core components (except LangChain for orchestration).


## Data Flow

### Complete Request Flow

```
┌─────────────────────────────────────────────────────────────┐
│ 1. USER SPEAKS                                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. voice/speech_recognition.py                              │
│    SpeechRecognizer.listen_streaming()                      │
│    • Captures audio                                         │
│    • Calls Google Speech API                                │
│    • Returns text                                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. agent.py                                                 │
│    Agent._handle_user_speech()                              │
│    • Checks if AI is speaking → Interrupt if yes           │
│    • Puts text in queue                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Queue (thread-safe)                                      │
│    Passes data between listening and processing threads     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. agent.py                                                 │
│    Agent._process_input_loop()                              │
│    • Gets text from queue                                   │
│    • Updates conversation history                           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. utils/history.py                                         │
│    ConversationHistory.add_user_message()                   │
│    • Stores message                                         │
│    • Trims to last N exchanges                              │
│    • Returns formatted context                              │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. chains/reasoning.py                                      │
│    ReasoningChains.analyze_and_respond()                    │
│    ┌────────────────────────────────────────────┐           │
│    │ CHAIN 1: Structured Reasoning              │           │
│    │ • Uses config/prompts.py template          │           │
│    │ • Calls Perplexity LLM                     │           │
│    │ • Parses to models/schemas.py HealthOverview│          │
│    └────────────────────────────────────────────┘           │
│    ┌────────────────────────────────────────────┐           │
│    │ CHAIN 2: Conversational Response           │           │
│    │ • Takes structured analysis                │           │
│    │ • Calls Perplexity LLM again               │           │
│    │ • Returns natural language                 │           │
│    └────────────────────────────────────────────┘           │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 8. utils/logger.py                                          │
│    Logger.structured_analysis()                             │
│    Logger.agent_response()                                  │
│    • Prints formatted output                                │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 9. utils/history.py                                         │
│    ConversationHistory.add_assistant_message()              │
│    • Stores AI response                                     │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 10. voice/text_to_speech.py                                 │
│     TextToSpeech.speak()                                    │
│     • Converts text to audio (gTTS)                         │
│     • Plays in 500ms chunks                                 │
│     • Checks interrupt flag each chunk                      │
└────────────────┬────────────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────────────────┐
│ 11. USER HEARS RESPONSE                                     │
│     (Can interrupt by speaking)                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Threading Model

```
┌──────────────────────────────────────────────────────────┐
│ MAIN THREAD                                              │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ agent._process_input_loop()                          │ │
│ │ • Gets from queue                                    │ │
│ │ • Calls LangChain (async/await)                      │ │
│ │ • Logs output                                        │ │
│ │ • Triggers TTS                                       │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ LISTENING THREAD (daemon)                                │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ agent._listen_loop()                                 │ │
│ │ • Continuously captures audio                        │ │
│ │ • Transcribes to text                                │ │
│ │ • Puts in queue                                      │ │
│ │ • Repeats                                            │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│ AUDIO PLAYBACK THREAD (daemon, on-demand)                │
│ ┌──────────────────────────────────────────────────────┐ │
│ │ TextToSpeech._play_audio()                           │ │
│ │ • Generates TTS                                      │ │
│ │ • Plays in chunks                                    │ │
│ │ • Checks interrupt flag                             │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘

         Communication: Thread-safe Queue
```
