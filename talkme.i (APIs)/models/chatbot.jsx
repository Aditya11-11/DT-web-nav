import React, { useState, useRef } from "react";

const Chatbot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState("");
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const silenceTimerRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const dataArrayRef = useRef(null);
  const sourceRef = useRef(null);
  const streamRef = useRef(null);

  const SILENCE_THRESHOLD = 0.01; // Adjust threshold (0-1)
  const SILENCE_DURATION = 2000; // 2 seconds silence

  // Toggle chatbot visibility
  const toggleChatbot = () => {
    setIsOpen(!isOpen);
  };

  // Send text message to /chat endpoint
  const sendTextMessage = async () => {
    if (!inputText.trim()) return;
    const userMsg = { sender: "user", text: inputText };
    setMessages((prev) => [...prev, userMsg]);

    try {
      const response = await fetch("http://localhost:5001/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ human_message: inputText }),
      });
      const data = await response.json();
      const botMsg = { sender: "bot", text: data.response };
      setMessages((prev) => [...prev, botMsg]);
    } catch (error) {
      console.error("Error sending text message:", error);
    }
    setInputText("");
  };

  // Start recording audio from the microphone with silence detection.
  const startRecording = async () => {
    if (recording) return;
    try {
      streamRef.current = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(streamRef.current);
      audioChunksRef.current = [];

      // Setup Web Audio API for silence detection.
      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      sourceRef.current = audioContextRef.current.createMediaStreamSource(streamRef.current);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      const bufferLength = analyserRef.current.frequencyBinCount;
      dataArrayRef.current = new Uint8Array(bufferLength);
      sourceRef.current.connect(analyserRef.current);

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorderRef.current.onstop = async () => {
        // Close the audio context and stop tracks.
        if (audioContextRef.current) {
          audioContextRef.current.close();
        }
        streamRef.current.getTracks().forEach(track => track.stop());

        // Create a Blob from the recorded audio
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        // Prepare FormData to send the audio file
        const formData = new FormData();
        formData.append("audio_file", audioBlob, "recording.wav");

        try {
          const response = await fetch("http://localhost:8000/voice_assistant", {
            method: "POST",
            body: formData,
          });
          const result = await response.json();
          // Append transcription and bot response messages
          setMessages(prev => [
            ...prev,
            { sender: "user", text: result.transcription },
            { sender: "bot", text: result.response }
          ]);
          // If audio URL is returned, play it
          if (result.audio_url) {
            const audio = new Audio("http://localhost:8000" + result.audio_url);
            audio.play();
          }
        } catch (error) {
          console.error("Error sending voice message:", error);
        }
        setRecording(false);
      };

      mediaRecorderRef.current.start();
      setRecording(true);
      monitorSilence();
    } catch (error) {
      console.error("Error accessing microphone:", error);
    }
  };

  // Monitor audio levels and auto-stop after silence.
  const monitorSilence = () => {
    if (!recording || !analyserRef.current) return;
    analyserRef.current.getByteTimeDomainData(dataArrayRef.current);
    const normalizedData = Array.from(dataArrayRef.current).map(
      (v) => Math.abs((v - 128) / 128)
    );
    const avgVolume = normalizedData.reduce((sum, v) => sum + v, 0) / normalizedData.length;

    if (avgVolume < SILENCE_THRESHOLD) {
      if (!silenceTimerRef.current) {
        silenceTimerRef.current = setTimeout(() => {
          if (recording) mediaRecorderRef.current.stop();
        }, SILENCE_DURATION);
      }
    } else {
      if (silenceTimerRef.current) {
        clearTimeout(silenceTimerRef.current);
        silenceTimerRef.current = null;
      }
    }
    setTimeout(monitorSilence, 200);
  };

  return (
    <div style={{ position: "fixed", bottom: "20px", right: "20px", zIndex: 1000 }}>
      <button
        onClick={toggleChatbot}
        title={isOpen ? "Close Chatbot" : "Open Chatbot"}
        style={{
          width: "60px",
          height: "60px",
          borderRadius: "50%",
          backgroundColor: "#578e7e",
          color: "#fff",
          border: "none",
          cursor: "pointer",
        }}
      >
        💬
      </button>

      {isOpen && (
        <div
          style={{
            position: "absolute",
            bottom: "70px",
            right: "0",
            width: "300px",
            height: "500px",
            backgroundColor: "#fff",
            borderRadius: "10px",
            boxShadow: "0px 4px 10px rgba(0,0,0,0.2)",
            display: "flex",
            flexDirection: "column",
            overflow: "hidden",
          }}
        >
          <div
            style={{
              backgroundColor: "#578e7e",
              color: "#fff",
              padding: "10px",
              textAlign: "center",
              fontWeight: "bold",
            }}
          >
            Voice Assistant
          </div>
          <div style={{ flex: 1, padding: "10px", overflowY: "auto" }}>
            {messages.map((msg, index) => (
              <div
                key={index}
                style={{
                  marginBottom: "10px",
                  textAlign: msg.sender === "user" ? "right" : "left",
                }}
              >
                <span
                  style={{
                    backgroundColor: msg.sender === "user" ? "#dcf8c6" : "#f1f0f0",
                    padding: "5px 10px",
                    borderRadius: "10px",
                    fontSize: "14px"
                  }}
                >
                  {msg.text}
                </span>
              </div>
            ))}
          </div>
          <div
            style={{
              padding: "10px",
              borderTop: "1px solid #ddd",
              display: "flex",
              alignItems: "center",
              gap: "5px"
            }}
          >
            <input
              type="text"
              placeholder="Type a message..."
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              style={{
                flex: 1,
                padding: "8px",
                fontSize: "14px",
                borderRadius: "20px",
                border: "1px solid #ccc"
              }}
            />
            {/* Microphone button: green when idle, red when recording */}
            <button
              onClick={startRecording}
              style={{
                width: "30px",
                height: "30px",
                borderRadius: "50%",
                backgroundColor: recording ? "#ff0000" : "#4CAF50",
                color: "#fff",
                border: "none",
                cursor: "pointer",
                fontSize: "16px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
              title="Speak"
            >
              {recording ? "●" : "🎤"}
            </button>
            {/* Send button with arrow icon */}
            <button
              onClick={sendTextMessage}
              style={{
                width: "35px",
                height: "35px",
                borderRadius: "50%",
                backgroundColor: "#578e7e",
                color: "#fff",
                border: "none",
                cursor: "pointer",
                fontSize: "18px",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
              title="Send"
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
