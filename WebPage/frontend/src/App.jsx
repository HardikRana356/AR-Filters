import { useRef, useState } from "react";
import Camera from "./Camera";
import "./ui.css";

export default function App() {
  const socketRef = useRef(new WebSocket("ws://127.0.0.1:8000/ws"));
  const [frame, setFrame] = useState("");
  const [camOn, setCamOn] = useState(true);

  const send = (obj) =>
    socketRef.current.send(JSON.stringify({ type: "command", ...obj }));

  return (
    <div className="app">
      <div className="sidebar">
        <h2>🎛 AR Dashboard</h2>

        <button className={camOn ? "on" : "off"} onClick={()=>{
          send({ action:"camera", value: !camOn });
          setCamOn(!camOn);
        }}>
          {camOn ? "Camera ON" : "Camera OFF"}
        </button>

        <hr />

        <button onClick={()=>send({action:"toggle",key:"eyes"})}>👓 Eyes</button>
        <button onClick={()=>send({action:"toggle",key:"face"})}>🎭 Face</button>
        <button onClick={()=>send({action:"toggle",key:"head"})}>👑 Head</button>
        <button onClick={()=>send({action:"toggle",key:"tears"})}>💧 Tears</button>

        <hr />

        <button onClick={()=>send({action:"next",key:"ei"})}>Next Eyes</button>
        <button onClick={()=>send({action:"next",key:"fi"})}>Next Face</button>
        <button onClick={()=>send({action:"next",key:"hi"})}>Next Head</button>
        <button onClick={()=>send({action:"next",key:"ti"})}>Next Tears</button>

        <hr/>
        <button onClick={()=>send({action:"bg",mode:"original"})}>Original BG</button>
<button onClick={()=>send({action:"bg",mode:"blur"})}>Blur BG</button>
<button onClick={()=>send({action:"bg",mode:"image"})}>Image BG</button>
<button onClick={()=>send({action:"next_bg"})}>Next Background</button>

      </div>

      <div className="viewer">
        <Camera socketRef={socketRef} onFrame={setFrame} camOn={camOn} />
        {frame && <img src={`data:image/jpeg;base64,${frame}`} />}
      </div>
    </div>
  );
}
