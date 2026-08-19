import api from "./axios";


// POST a newly created Form to save
export async function processVoice({formID, audio}) {
    try {
        // Create form data container
        const formData = new FormData();
        
        // Key must match the 'audio' parameter name in FastAPI
        formData.append("audio", audio);

        const response = await api.post(`/api/voice/forms/${formID}/fill`, 
                                        formData, 
                                        {
                                            headers: {"Content-Type": "multipart/form-data",},
                                        });
        return response.data;
    } catch (error) {
        console.error("Failed to fetch Whisper and LLM Results:", error);
        throw error;
    }
}
