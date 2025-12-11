expot default function Home() {
  return (
    <div style={{ padding: "50px", fontFamily: "sans-serif" }}>
      <h1>The Self-Healing Demo<h1>
      <p>System Status: ONLINE</p>

      {Math.random() > 0.5 ? (
        <p>Lucky Number!</p>
      ) : (
        <p>Try again.</p> 
      )}
    </dive>
  );
}
