export default function ControlPanel({ send }) {
  const btn = (label, cmd) => (
    <button onClick={() => send(cmd)}>{label}</button>
  );

  return (
    <div style={{ padding: 10 }}>
      <h3>Controls</h3>

      {btn("Eyes", { action: "toggle", key: "eyes_on" })}
      {btn("Face", { action: "toggle", key: "face_on" })}
      {btn("Head", { action: "toggle", key: "head_on" })}
      {btn("Tears", { action: "toggle", key: "tears_on" })}

      <hr />

      {btn("Next Eyes", { action: "next", key: "eyes_i" })}
      {btn("Next Face", { action: "next", key: "face_i" })}
      {btn("Next Head", { action: "next", key: "head_i" })}
      {btn("Next Tears", { action: "next", key: "tears_i" })}

      <hr />

      {btn("Original BG", { action: "bg", mode: "original" })}
      {btn("Image BG", { action: "bg", mode: "image" })}
      {btn("Blur BG", { action: "bg", mode: "blur" })}
    </div>
  );
  send(JSON.stringify({
  type: "command",
  action: "toggle",
  key: "eyes_on"
}));

}
