class Chatbot {
    constructor() {
        this.url = 'http://localhost:8000';
        this.prompt = document.querySelector('#prompt');
        this.sendbtn = document.querySelector('#send');
        this.voicebtn = document.querySelector('#voice');
        this.usersend = true;
        this.delaytime = 5000;
        this.recordingstatus = false;
        this.display = document.querySelector('#display');
        this.togglebtn = document.querySelector('#toggle-btn');
        this.togglebtn.addEventListener('click',()=>{
            var chatbot = document.querySelector('.chatbot').style;
            if (chatbot.display != 'none') {
                chatbot.display = 'none';
                
            } else {
                chatbot.display = '';
            }
            

        });
        this.sendbtn.addEventListener('click', () => {
            if (this.usersend) {
                this.usersend = false;
                this.do();
                this.mediaRecorder;
                this.audioChunks = [];
            }
        });
        this.voicebtn.addEventListener('click', () => {
            if (!this.recordingstatus) {
                this.recordingstatus = true;
                this.voicebtn.innerHTML = '⏸️';
                this.recordstart();
            } else {
                this.recordingstatus = false;
                this.voicebtn.innerHTML = '▶️';
                this.recordstop();
            }
        });
    }

    async getchatdata(message) {
        try {
            const response = await fetch(`${this.url}/chat`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ "human_message": message }),
            });
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            const data = await response.json(); 
            return data;
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }
    async do() {
        var userinput = this.prompt.value;
        this.addhumanchat(userinput)
        var data = await this.getchatdata(userinput);
        this.addbotchat(data['response']);
        this.usersend = true
        if (data['redirect_url']){
            setTimeout(function() {
                window.location.href =data['redirect_url'];

            }, this.delaytime);
        }
        // redirect if condition\/

    }
    addhumanchat(message) {
        var content = `
        <div class="chatbot-chatbar" >
        <div class="chatbot-chat chatbot-user">${message}</div>
        </div>`
        this.display.innerHTML += content;
        this.display.scrollTop = this.display.scrollHeight;

    }
    addbotchat(message) {
        var content = `
        <div class="chatbot-chatbar" >
        <div class="chatbot-chat chatbot-bot">${message}</div>
        </div>`
        this.display.innerHTML += content;
        this.display.scrollTop = this.display.scrollHeight;

    }

    async recordstart() {
        try {
            // Request microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];

            this.mediaRecorder.start();
            console.log("Recording started");

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data && event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };
            this.mediaRecorder.onstop = async () => {
                const webmBlob = new Blob(this.audioChunks, { type: 'audio/webm' });
                const wavBlob = await this.convertWebMtoWav(webmBlob);
                this.playaud(wavBlob);

            };
        }
        catch (error) {
            console.error("Error accessing microphone:", error);
        }
    };

    recordstop() {
        if (this.mediaRecorder && this.mediaRecorder.state !== "inactive") {
            this.mediaRecorder.stop();
        }
    }

    async playaud(audioBlob) {
        try {
            const formData = new FormData();
            console.log("File Type:", audioBlob.type);
            console.log("File Size:", audioBlob.size);
            formData.append('audio_file', audioBlob, 'audio.wav');  // ✅ Correct key
            const response = await fetch(`${this.url}/voice_assistant`, {
                method: 'POST',
                body: formData,
            });
            console.log("send");

            if (response.ok) {
                const data = await response.json();
                console.log(data);
                this.addhumanchat(data.transcription);
                this.addbotchat(data.response);
                const audioElement = new Audio(`${this.url}${data.audio_url}`);
                audioElement.play();
                if (data['redirect_url']){
                    setTimeout(function() {
                        window.location.href =data['redirect_url'];
        
                    }, this.delaytime);
                }
            } else {
                console.error('Upload failed:', response.statusText);
            }
        } catch (error) {
            console.error('Error during file upload:', error);
        }
    }

    async convertWebMtoWav(webmBlob) {
        const audioContext = new AudioContext();
        const arrayBuffer = await webmBlob.arrayBuffer();
        const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

        const numOfChannels = audioBuffer.numberOfChannels;
        const sampleRate = audioBuffer.sampleRate;
        const length = audioBuffer.length * numOfChannels * 2 + 44;
        const buffer = new ArrayBuffer(length);
        const view = new DataView(buffer);

        // WAV Header
        const writeString = (offset, string) => {
            for (let i = 0; i < string.length; i++) {
                view.setUint8(offset + i, string.charCodeAt(i));
            }
        };

        writeString(0, 'RIFF');
        view.setUint32(4, 36 + audioBuffer.length * numOfChannels * 2, true);
        writeString(8, 'WAVE');
        writeString(12, 'fmt ');
        view.setUint32(16, 16, true);
        view.setUint16(20, 1, true);
        view.setUint16(22, numOfChannels, true);
        view.setUint32(24, sampleRate, true);
        view.setUint32(28, sampleRate * numOfChannels * 2, true);
        view.setUint16(32, numOfChannels * 2, true);
        view.setUint16(34, 16, true);
        writeString(36, 'data');
        view.setUint32(40, audioBuffer.length * numOfChannels * 2, true);

        // Interleave channels
        const interleaved = new Float32Array(audioBuffer.length * numOfChannels);
        for (let i = 0, j = 0; i < audioBuffer.length; i++) {
            for (let channel = 0; channel < numOfChannels; channel++) {
                interleaved[j++] = audioBuffer.getChannelData(channel)[i];
            }
        }

        // Convert to PCM
        let offset = 44;
        for (let i = 0; i < interleaved.length; i++, offset += 2) {
            view.setInt16(offset, interleaved[i] * 0x7FFF, true);
        }

        return new Blob([view], { type: 'audio/wav' });
    }


};

document.addEventListener("DOMContentLoaded", () => {
    const chatbot = new Chatbot();
});