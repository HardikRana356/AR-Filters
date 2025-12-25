import { useEffect, useRef } from "react";

export default function Camera({ socketRef, onFrame, camOn }) {
  const video = useRef(null);

  useEffect(() => {
    if (!camOn) return;

    navigator.mediaDevices.getUserMedia({ video: true })
      .then(s => video.current.srcObject = s);
  }, [camOn]);

  useEffect(() => {
    if (!camOn) return;

    socketRef.current.onmessage = e => onFrame(e.data);

    const id = setInterval(() => {
      if (!camOn || socketRef.current.readyState !== 1) return;
      const c = document.createElement("canvas");
      c.width = 640; c.height = 480;
      c.getContext("2d").drawImage(video.current, 0, 0);
      socketRef.current.send(JSON.stringify({
        type:"frame",
        data:c.toDataURL("image/jpeg").split(",")[1]
      }));
    }, 90);

    return () => clearInterval(id);
  }, [camOn]);

  return <video ref={video} autoPlay hidden />;
}
