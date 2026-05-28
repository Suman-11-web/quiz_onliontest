async function move() {
    if (cur < questions.length - 1) { 
        cur++; 
        render(); 
    } else { 
        document.getElementById('q-text').innerText = "Connecting to Server..."; 
        
        try {
            await fetch('/save_score', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'same-origin',
                body: JSON.stringify({ score: score, total: questions.length })
            });
        } catch (err) {
            console.log("Server error:", err);
        }

        // Updated for the Dark Neon Theme
        document.querySelector('.main-card').innerHTML = `
            <h2 class="epic-title" style="margin-bottom: 10px;">QUEST COMPLETE</h2>
            <h1 style="color: #f8fafc; font-size: 4rem; margin: 10px 0; text-shadow: 0 0 20px rgba(255,255,255,0.3);">${score}/${questions.length}</h1>
            <p style="color: #00f2fe; font-weight: 800; letter-spacing: 2px; margin-bottom: 30px;">SCORE SAVED TO MAINFRAME</p>
            <button class="btn-login" onclick="location.reload()">RETRY ARENA</button>
        `;
    }
}
