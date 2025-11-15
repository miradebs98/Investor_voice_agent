class VCAgentClient {
    constructor() {
        this.ws = null;
        this.isRecording = false;
        this.recognition = null;
        this.userInteracted = false; // Track if user has interacted
        this.pendingAudio = null; // Store audio that needs user interaction
        this.initializeElements();
        this.setupEventListeners();
    }

    initializeElements() {
        this.recordButton = document.getElementById('recordButton');
        this.resetButton = document.getElementById('resetButton');
        this.messagesContainer = document.getElementById('messages');
        this.statusText = document.getElementById('statusText');
        this.statusIndicator = document.getElementById('statusIndicator');
    }

    setupEventListeners() {
        this.recordButton.addEventListener('click', () => this.toggleRecording());
        this.resetButton.addEventListener('click', () => this.resetConversation());
    }

    connect() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;
        
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('Connected to server');
            this.updateStatus('Connected. Click "Start Recording" to begin');
            this.recordButton.disabled = false;
            this.statusIndicator.classList.add('active');
        };

        this.ws.onmessage = async (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'audio') {
                // Always use free animated avatar (ignore D-ID/HeyGen)
                if (data.avatar_image_url) {
                    this.setupFreeAvatar(data.avatar_image_url);
                }
                
                // Always show the message text
                this.addMessage(data.text, 'vc');
                
                // Only play audio if user has interacted, otherwise store it
                if (this.userInteracted) {
                    try {
                        await this.playAudio(data.data);
                    } catch (error) {
                        console.warn('Audio playback failed:', error);
                        // Audio failed but message is already shown, so continue
                    }
                    this.updateStatus('Ready for your next response');
                } else {
                    // Store audio for later playback after user interaction
                    this.pendingAudio = data.data;
                    this.updateStatus('Click "Start Recording" to begin');
                }
            } else if (data.type === 'user_message') {
                this.addMessage(data.text, 'user');
                this.updateStatus('VC is thinking...');
            } else if (data.type === 'text_error') {
                this.addMessage(data.text, 'vc');
                this.updateStatus('Error occurred. Please try again.');
            }
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateStatus('Connection error. Reconnecting...');
        };

        this.ws.onclose = (event) => {
            console.log('Disconnected from server. Code:', event.code, 'Reason:', event.reason);
            this.updateStatus('Disconnected. Reconnecting...');
            this.statusIndicator.classList.remove('active');
            this.recordButton.disabled = true;
            // Reconnect after 2 seconds
            setTimeout(() => {
                console.log('Attempting to reconnect...');
                this.connect();
            }, 2000);
        };
    }

    async toggleRecording() {
        if (!this.isRecording) {
            await this.startRecording();
        } else {
            await this.stopRecording();
        }
    }

    async startRecording() {
        // Mark user as interacted (allows audio playback)
        this.userInteracted = true;
        
        // Play any pending audio (like welcome message)
        if (this.pendingAudio) {
            try {
                await this.playAudio(this.pendingAudio);
                this.pendingAudio = null;
            } catch (error) {
                console.warn('Failed to play pending audio:', error);
            }
        }
        
        try {
            // Check if browser supports Speech Recognition
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            
            if (!SpeechRecognition) {
                alert('Your browser does not support speech recognition. Please use Chrome or Edge.');
                return;
            }

            this.recognition = new SpeechRecognition();
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';

            this.recognition.onstart = () => {
                this.isRecording = true;
                this.recordButton.classList.add('recording');
                this.recordButton.querySelector('.btn-text').textContent = 'Stop Recording';
                this.statusIndicator.classList.add('listening');
                this.statusIndicator.classList.remove('active');
                this.updateStatus('Listening... Speak now!');
            };

            this.recognition.onresult = async (event) => {
                const transcript = event.results[0][0].transcript;
                console.log('Speech recognition result:', transcript);
                if (transcript.trim()) {
                    this.updateStatus('Sending your pitch...');
                    await this.sendTranscript(transcript);
                } else {
                    console.warn('Empty transcript received');
                }
            };

            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.updateStatus(`Error: ${event.error}`);
                this.stopRecording();
            };

            this.recognition.onend = () => {
                console.log('Speech recognition ended');
                // Don't stop recording immediately - wait a bit for onresult to fire
                setTimeout(() => {
                    this.stopRecording();
                }, 100);
            };

            this.recognition.start();
        } catch (error) {
            console.error('Error starting recording:', error);
            this.updateStatus('Error: Could not access microphone');
            alert('Please allow microphone access to use this feature.');
        }
    }

    async stopRecording() {
        if (this.recognition) {
            this.recognition.stop();
        }
        this.isRecording = false;
        this.recordButton.classList.remove('recording');
        this.recordButton.querySelector('.btn-text').textContent = 'Start Recording';
        this.statusIndicator.classList.remove('listening');
        this.statusIndicator.classList.add('active');
        this.updateStatus('Processing your pitch...');
    }

    async sendTranscript(transcript) {
        if (!this.ws) {
            console.error('WebSocket is null');
            this.updateStatus('Connection lost. Please refresh.');
            return;
        }
        
        if (this.ws.readyState === WebSocket.OPEN) {
            const message = {
                type: 'text',
                text: transcript
            };
            console.log('Sending transcript:', message);
            try {
                this.ws.send(JSON.stringify(message));
                console.log('✅ Transcript sent successfully');
            } catch (error) {
                console.error('❌ Error sending transcript:', error);
                this.updateStatus('Failed to send message. Please try again.');
            }
        } else {
            console.error('WebSocket not open. State:', this.ws.readyState, '(1=OPEN, 0=CONNECTING, 2=CLOSING, 3=CLOSED)');
            this.updateStatus('Connection lost. Please refresh the page.');
        }
    }

    async playAudio(base64Audio) {
        return new Promise((resolve, reject) => {
            const audio = new Audio(`data:audio/mpeg;base64,${base64Audio}`);
            
            // Simple: start animation when audio plays
            this.startSpeakingAnimation();
            
            audio.onended = () => {
                this.stopSpeakingAnimation();
                resolve();
            };
            audio.onerror = (error) => {
                console.error('Audio playback error:', error);
                this.stopSpeakingAnimation();
                resolve();
            };
            
            // Try to play, handle autoplay restrictions
            const playPromise = audio.play();
            if (playPromise !== undefined) {
                playPromise
                    .then(() => {
                        // Audio started playing - animation is already active
                    })
                    .catch(error => {
                        // Autoplay was prevented - this is okay, user will interact
                        console.warn('Audio autoplay prevented:', error);
                        this.stopSpeakingAnimation();
                        resolve();
                    });
            }
        });
    }
    
    startSpeakingAnimation() {
        const animatedAvatar = document.getElementById('animatedAvatar');
        if (animatedAvatar) {
            animatedAvatar.classList.add('speaking');
        }
    }
    
    stopSpeakingAnimation() {
        const animatedAvatar = document.getElementById('animatedAvatar');
        if (animatedAvatar) {
            animatedAvatar.classList.remove('speaking');
        }
    }
    
    setupFreeAvatar(imageUrl) {
        // Setup free animated avatar with user's image
        if (!imageUrl) {
            return; // No image URL provided
        }
        
        const avatarCircle = document.getElementById('avatarCircle');
        const animatedAvatar = document.getElementById('animatedAvatar');
        const avatarImage = document.getElementById('avatarImage');
        const heygenAvatar = document.getElementById('heygenAvatar');
        
        if (animatedAvatar && avatarImage) {
            // Hide other avatars
            if (avatarCircle) {
                avatarCircle.style.display = 'none';
            }
            if (heygenAvatar) {
                heygenAvatar.style.display = 'none';
            }
            
            // Show and setup animated avatar
            avatarImage.src = imageUrl;
            animatedAvatar.style.display = 'block';
            console.log('✅ Free animated avatar setup with image:', imageUrl);
        }
    }

    addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'vc' ? 'AV' : 'You';
        
        const content = document.createElement('div');
        content.className = 'message-content';
        const p = document.createElement('p');
        p.textContent = text;
        content.appendChild(p);
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(content);
        
        this.messagesContainer.appendChild(messageDiv);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    resetConversation() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({ type: 'reset' }));
        }
        this.messagesContainer.innerHTML = '';
        this.updateStatus('Starting new pitch session...');
    }

    updateStatus(text) {
        this.statusText.textContent = text;
    }

    setupAvatar(embedUrl, avatarType) {
        // Skip D-ID/HeyGen - we're using free animated avatar instead
        // This function is kept for backwards compatibility but won't be called
        console.log('D-ID/HeyGen avatar disabled - using free animated avatar instead');
    }
}

// Initialize the client when page loads
window.addEventListener('DOMContentLoaded', () => {
    const client = new VCAgentClient();
    client.connect();
});

