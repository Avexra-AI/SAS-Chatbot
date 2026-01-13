import { useState } from "react";
import { askQuestion } from "../api/chatApi";
import ChartRenderer from "../components/ChartRenderer";

function ChatPage() {
  const [input, setInput] = useState("");
  const [response, setResponse] = useState(null);

  const handleAsk = async () => {
    const res = await askQuestion(input);
    setResponse(res.answer);
  };

  return (
    <div>
      <h2>Sales Analytics Assistant</h2>

      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Ask a question..."
      />
      <button onClick={handleAsk}>Ask</button>

      {/* ✅ Always show NL answer */}
      {response?.answer && (
        <p><strong>Answer:</strong> {response.answer}</p>
      )}

      {/* 📊 Chart only when valid */}
      <ChartRenderer
        visualization={response?.visualization}
        data={response?.data}
      />
    </div>
  );
}

export default ChatPage;
