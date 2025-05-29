import streamlit as st
import streamlit.components.v1 as components

# Streamlit UI
st.set_page_config(page_title="Flappy Runner", layout="centered")
st.title("🏃‍➡️ Flappy Runner - Streamlit Edition")

# Game controls
speed = st.slider("Game Speed (1 = Slow, 10 = Fast)", 1, 10, 3)
difficulty = st.selectbox("Difficulty Level", ["Easy", "Medium", "Hard"])

# Base pipe gap values for each difficulty + an additional 60 pixels for a bigger gap
pipe_gap_value = {"Easy": 180 + 60, "Medium": 130 + 60, "Hard": 100 + 60}[difficulty]

components.html(
    rf"""
    <style>
    html, body {{
        margin: 0;
        padding: 0;
        overflow: hidden;
        height: 100%;
        width: 100%;
    }}
    canvas {{
        display: block;
        margin: auto;
        border: 2px solid black;
        /* Background handled by JS gradients */
    }}
    #gameOverScreen, #countdown {{
        position: absolute;
        top: 200px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0, 0, 0, 0.75);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        z-index: 20; /* Ensure it's above everything */
    }}
    #scoreDisplay {{
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-family: 'Press Start 2P', cursive; /* A pixel-art font if available, or a bold sans-serif */
        font-size: 20px; /* Adjusted size */
        font-weight: bold;
        color: #FFF; /* White text */
        background: rgba(0, 0, 0, 0.6); /* Slightly darker, more prominent background */
        padding: 8px 20px; /* More padding */
        border-radius: 8px;
        border: 2px solid #FFD700; /* Gold border for personality */
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8); /* Text shadow for depth */
        box-shadow: 0px 0px 15px rgba(255, 215, 0, 0.5); /* Glowing box shadow */
        z-index: 10; /* Ensure it's on top */
    }}
    /* Import Google Font for the score */
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    </style>

    <canvas id="gameCanvas" width="400" height="600"></canvas>
    <div id="countdown" style="display:none;">Ready?</div>
    <div id="gameOverScreen" style="display:none;">
        <h2>💥 Game Over</h2>
        <p id="finalScoreText"></p>
        <p id="highScoreText"></p>
        <button onclick="startGame()">🔁 Retry</button>
    </div>
    <div id="scoreDisplay">Score: 0 | 🏆 High: 0</div>

    <script>
    const canvas = document.getElementById("gameCanvas");
    const ctx = canvas.getContext("2d");

    let birdY = 250;
    let velocity = 0;
    const gravity = 0.5;
    const flapStrength = -8;
    const birdX = 80;
    const birdSize = 30;

    const birdEmote = "🕊️"; // Using bird emote from second code

    let pipes = [];
    const pipeWidth = 70; // From first code
    const pipeGap = {pipe_gap_value}; // From Streamlit slider

    let frame = 0;
    let score = 0;
    let highScore = 0;
    let gameRunning = false;
    let paused = false;
    let ready = false;
    let currentPipeSpeed; // Use a distinct variable for current pipe speed

    // Removed speedIncreaseRate as it led to unexpected acceleration

    // Variables for clouds (from second code)
    let clouds = [];
    const cloudEmote = "☁️";
    const cloudSize = 40; // Base size for clouds
    const cloudMinSize = 25; // Minimum cloud size
    const cloudMaxSize = 60; // Maximum cloud size

    // New variables for multiple grass layers and ground (from second code)
    let grassesForeground = [];
    const grassEmoteFG = "🌿";
    const grassSizeFG = 45; // Base size for foreground grass

    let grassesMidground = [];
    const grassEmoteMG = "🌱";
    const grassSizeMG = 35; // Base size for midground grass

    let grassesBackground = [];
    const grassEmoteBG = "🍃";
    const grassSizeBG = 25; // Base size for background grass

    const groundHeight = 100; // Height of the solid ground block (from second code)

    const gameOverScreen = document.getElementById("gameOverScreen");
    const finalScoreText = document.getElementById("finalScoreText");
    const highScoreText = document.getElementById("highScoreText");
    const scoreDisplay = document.getElementById("scoreDisplay");
    const countdownDiv = document.getElementById("countdown");

    // Sounds (from first code)
    const jumpSound = new Audio("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg");
    const scoreSound = new Audio('https://audio.jukehost.co.uk/MvoNNWrjBKFfMnyOBYiGU54EWAJiC3gm');
    const gameOverSound = new Audio('https://audio.jukehost.co.uk/0QTMOfboi9npdAqvnssGZFrsi6GTOnlg');
    const bgMusic = new Audio("https://audio.jukehost.co.uk/8LnIiGnXtdZCrfq8jkEJBrDWyQ12ZxyO");
    bgMusic.loop = true;

    // Prevent default for specific keys (from first code)
    window.addEventListener("keydown", function(e) {{
        if (["ArrowUp", " ", "w", "W"].includes(e.key)) {{
            e.preventDefault();
        }}
    }}, false);

    // Keydown event listener (from first code, adapted)
    document.addEventListener("keydown", function(e) {{
        if (["ArrowUp", " ", "w", "W"].includes(e.key)) {{
            if (gameRunning && !paused && ready) {{
                velocity = flapStrength;
                jumpSound.play();
            }} else if (!gameRunning && e.key === " ") {{
                startGame();
            }}
        }} else if (e.key.toLowerCase() === "p") {{
            e.preventDefault();
            if (gameRunning && ready) {{
                paused = !paused;
                if (!paused) {{
                    bgMusic.play();
                    gameLoop();
                }} else {{
                    bgMusic.pause();
                }}
            }}
        }}
    }}, false);

    // Touch event listener (from first code)
    document.addEventListener("touchstart", function(e) {{
        e.preventDefault();
        if (gameRunning && !paused && ready) {{
            velocity = flapStrength;
            jumpSound.play();
        }}
    }}, {{ passive: false }});

    // Draw bird (from second code)
    function drawBird() {{
        ctx.font = `${{birdSize}}px serif`;
        ctx.save(); // Save the current canvas state

        ctx.translate(birdX + birdSize / 2, birdY);
        ctx.scale(-1, 1); // Flip horizontally

        ctx.fillText(birdEmote, -(birdSize / 2), birdSize / 4);

        ctx.restore(); // Restore the canvas to its original state
    }}

    // Draw background (from second code)
    function drawBackground() {{
        // Draw Sky Gradient (darker at top, lighter at bottom)
        const skyGradient = ctx.createLinearGradient(0, 0, 0, canvas.height - groundHeight);
        skyGradient.addColorStop(0, "#6A5ACD"); // Darker blue at the top
        skyGradient.addColorStop(1, "#87CEEB"); // Lighter sky blue towards the horizon
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height - groundHeight); // Fill sky area

        // Draw Ground Gradient (field)
        const groundGradient = ctx.createLinearGradient(0, canvas.height - groundHeight, 0, canvas.height);
        groundGradient.addColorStop(0, "#6B8E23"); // Lighter at the top of the field (Olive Drab)
        groundGradient.addColorStop(1, "#2E8B57"); // Darker towards the bottom/foreground (Sea Green)
        ctx.fillStyle = groundGradient;
        ctx.fillRect(0, canvas.height - groundHeight, canvas.width, groundHeight); // Fill ground area
    }}

    // Draw pipes (from second code)
    function drawPipes() {{
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)'; // Add a subtle shadow to pipes
        ctx.shadowBlur = 5;
        ctx.shadowOffsetX = 3;
        ctx.shadowOffsetY = 3;

        pipes.forEach(pipe => {{
            ctx.fillStyle = "#228B22";
            ctx.fillRect(pipe.x, 0, pipeWidth, pipe.top);
            ctx.fillRect(pipe.x, pipe.top + pipeGap, pipeWidth, canvas.height - pipe.top - pipeGap);

            ctx.fillStyle = "#3CB371";
            ctx.fillRect(pipe.x, 0, pipeWidth / 4, pipe.top);
            ctx.fillRect(pipe.x, pipe.top + pipeGap, pipeWidth / 4, canvas.height - pipe.top - pipeGap);

            ctx.fillStyle = "#006400";
            ctx.fillRect(pipe.x + pipeWidth * 0.75, 0, pipeWidth / 4, pipe.top);
            ctx.fillRect(pipe.x + pipeWidth * 0.75, pipe.top + pipeGap, pipeWidth / 4, canvas.height - pipe.top - pipeGap);

            ctx.fillStyle = "#90EE90";
            ctx.fillRect(pipe.x, pipe.top - 5, pipeWidth, 5);
            ctx.fillRect(pipe.x, pipe.top + pipeGap - 5, pipeWidth, 5); // Corrected cap for lower pipe
        }});
        ctx.shadowBlur = 0; // Reset shadow for other elements
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
    }}

    // Update pipes (combined from both codes, adjusted speed)
    function updatePipes() {{
        // Pipe generation based on pixel distance travelled (from first code)
        if (pipes.length === 0 || (canvas.width - pipes[pipes.length - 1].x) >= 250) {{
            const minTop = 50;
            const maxTop = canvas.height - pipeGap - groundHeight - 50; // Adapted from second code, considering ground
            if (maxTop < minTop) {{ // Safety check for very small canvas/large gap
                const adjustedMaxTop = minTop + 20;
                const top = Math.random() * (adjustedMaxTop - minTop) + minTop;
                pipes.push({{ x: canvas.width, top: top, scored: false }}); // Add scored flag
            }} else {{
                const top = Math.random() * (maxTop - minTop) + minTop;
                pipes.push({{ x: canvas.width, top: top, scored: false }}); // Add scored flag
            }}
        }}

        pipes.forEach(pipe => pipe.x -= currentPipeSpeed); // Use constant currentPipeSpeed
        pipes = pipes.filter(pipe => pipe.x + pipeWidth > 0);
    }}

    // Helper function to check for overlap with pipes for grass (from second code)
    function isOverlappingPipes(entityX, entityY, entityWidth, entityHeight) {{
        for (let pipe of pipes) {{
            if (entityX < pipe.x + pipeWidth && entityX + entityWidth > pipe.x) {{
                const entityTop = entityY - entityHeight;
                const entityBottom = entityY;

                const pipeTopEdge = 0;
                const pipeBottomEdge = canvas.height;

                if (
                    (entityBottom > pipeTopEdge && entityTop < pipe.top) ||
                    (entityBottom > pipe.top + pipeGap && entityTop < pipeBottomEdge)
                ) {{
                    return true;
                }}
            }}
        }}
        return false;
    }}

    // Functions for clouds (from second code)
    function drawClouds() {{
        clouds.forEach(cloud => {{
            const relativeY = cloud.y;
            const skyHeight = canvas.height - groundHeight;
            const scaleFactor = 0.5 + (relativeY / skyHeight * 0.5);
            const currentCloudSize = Math.max(cloudMinSize, Math.min(cloudMaxSize, cloudSize * scaleFactor));

            ctx.font = `${{currentCloudSize}}px serif`;
            ctx.fillText(cloudEmote, cloud.x, cloud.y);
        }});
    }}

    function updateClouds() {{
        if (frame % 70 === 0) {{
            const x = canvas.width + Math.random() * 100;
            const y = Math.random() * (canvas.height / 2 - cloudSize / 2) + 20;
            clouds.push({{ x: x, y: y }});
        }}
        clouds.forEach(cloud => cloud.x -= 0.5);
        clouds = clouds.filter(cloud => cloud.x + cloudMaxSize > 0);
    }}

    // Functions for Foreground Grass (from second code)
    function drawGrassesForeground() {{
        grassesForeground.forEach(grass => {{
            const relativeY = grass.y - (canvas.height - groundHeight);
            const adjustedScale = 0.5 + (relativeY / (groundHeight * 1.5));
            const finalScale = Math.max(0.5, Math.min(1.2, adjustedScale));
            const currentSize = grassSizeFG * finalScale;
            ctx.font = `${{currentSize}}px serif`;
            ctx.fillText(grassEmoteFG, grass.x, grass.y);
        }});
    }}

    function updateGrassesForeground() {{
        if (frame % 5 === 0) {{
            const x = canvas.width + Math.random() * 20;
            const minGrassY = (canvas.height - groundHeight + (grassSizeFG * 0.1));
            const maxGrassY = canvas.height + (grassSizeFG * 0.3);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeFG * 0.05)));

            if (!isOverlappingPipes(x, actualY, grassSizeFG, grassSizeFG)) {{
                grassesForeground.push({{ x: x, y: actualY }});
            }}
        }}
        grassesForeground.forEach(grass => grass.x -= (currentPipeSpeed * 1.2)); // Scale grass speed with currentPipeSpeed
        grassesForeground = grassesForeground.filter(grass => grass.x > -grassSizeFG);
    }}

    // Functions for Midground Grass (from second code)
    function drawGrassesMidground() {{
        grassesMidground.forEach(grass => {{
            const relativeY = grass.y - (canvas.height - groundHeight);
            const adjustedScale = 0.5 + (relativeY / (groundHeight * 1.5));
            const finalScale = Math.max(0.5, Math.min(1.2, adjustedScale));
            const currentSize = grassSizeMG * finalScale;
            ctx.font = `${{currentSize}}px serif`;
            ctx.fillText(grassEmoteMG, grass.x, grass.y);
        }});
    }}

    function updateGrassesMidground() {{
        if (frame % 10 === 0) {{
            const x = canvas.width + Math.random() * 30;
            const minGrassY = (canvas.height - groundHeight + (grassSizeMG * 0.1));
            const maxGrassY = canvas.height + (grassSizeMG * 0.2);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeMG * 0.05)));

            if (!isOverlappingPipes(x, actualY, grassSizeMG, grassSizeMG)) {{
                grassesMidground.push({{ x: x, y: actualY }});
            }}
        }}
        grassesMidground.forEach(grass => grass.x -= (currentPipeSpeed * 0.8)); // Scale grass speed with currentPipeSpeed
        grassesMidground = grassesMidground.filter(grass => grass.x > -grassSizeMG);
    }}

    // Functions for Background Grass/Foliage (from second code)
    function drawGrassesBackground() {{
        grassesBackground.forEach(grass => {{
            const relativeY = grass.y - (canvas.height - groundHeight);
            const adjustedScale = 0.5 + (relativeY / (groundHeight * 1.5));
            const finalScale = Math.max(0.5, Math.min(1.2, adjustedScale));
            const currentSize = grassSizeBG * finalScale;
            ctx.font = `${{currentSize}}px serif`;
            ctx.fillText(grassEmoteBG, grass.x, grass.y);
        }});
    }}

    function updateGrassesBackground() {{
        if (frame % 20 === 0) {{
            const x = canvas.width + Math.random() * 40;
            const minGrassY = (canvas.height - groundHeight + (grassSizeBG * 0.05));
            const maxGrassY = canvas.height + (grassSizeBG * 0.1);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeBG * 0.02)));

            if (!isOverlappingPipes(x, actualY, grassSizeBG, grassSizeBG)) {{
                grassesBackground.push({{ x: x, y: actualY }});
            }}
        }}
        grassesBackground.forEach(grass => grass.x -= (currentPipeSpeed * 0.6)); // Scale grass speed with currentPipeSpeed
        grassesBackground = grassesBackground.filter(grass => grass.x > -grassSizeBG);
    }}


    // Hitbox tweaks for better alignment (from first code)
    const hitboxOffsetX = 0;
    const hitboxOffsetY = -10;
    const hitboxWidth = birdSize - 16;
    const hitboxHeight = birdSize - 15;

    // Check collision (combined from both codes)
    function checkCollision() {{
        for (let pipe of pipes) {{
            if (
                birdX + hitboxOffsetX + hitboxWidth > pipe.x &&
                birdX + hitboxOffsetX < pipe.x + pipeWidth
            ) {{
                if (
                    birdY + hitboxOffsetY < pipe.top ||
                    birdY + hitboxOffsetY + hitboxHeight > pipe.top + pipeGap
                ) return true;
            }}
        }}
        // Collision with ground (from second code, adapted for birdY and groundHeight)
        if (birdY + birdSize > canvas.height - groundHeight) return true;
        // Collision with top of canvas (from first code)
        return birdY < 0;
    }}

    // Draw score (from first code)
    function drawScore() {{
        scoreDisplay.innerText = `Score: ${{score}} | 🏆 High: ${{highScore}}`;
    }}

    // Show game over screen (combined from both codes)
    function showGameOver() {{
        gameRunning = false;
        gameOverSound.play(); // From first code
        gameOverScreen.style.display = "block";
        finalScoreText.textContent = "You scored " + score + " points!";
        if (score > highScore) {{
            highScore = score;
            localStorage.setItem("flappyRunnerHighScore", highScore); // From first code
        }}
        highScoreText.textContent = "High Score: " + highScore;
        bgMusic.pause(); // From first code
    }}

    // Load high score from local storage (from first code)
    function loadHighScore() {{
        const storedHighScore = localStorage.getItem("flappyRunnerHighScore");
        if (storedHighScore) {{
            highScore = parseInt(storedHighScore);
        }}
    }}

    // Game loop (combined logic and drawing order)
    function gameLoop() {{
        if (!gameRunning || paused || !ready) return; // From first code

        drawBackground(); // From second code

        updateClouds(); // From second code
        drawClouds(); // From second code
        updateGrassesBackground(); // From second code
        drawGrassesBackground(); // From second code

        updatePipes(); // Combined
        drawPipes(); // From second code
        updateGrassesMidground(); // From second code
        drawGrassesMidground(); // From second code

        drawBird(); // From second code

        updateGrassesForeground(); // From second code
        drawGrassesForeground(); // From second code

        drawScore(); // From first code

        velocity += gravity;
        birdY += velocity;

        // Removed gameSpeed += speedIncreaseRate; to prevent unexpected acceleration

        // Score update logic (from first code)
        pipes.forEach(pipe => {{
            if (pipe.x + pipeWidth < birdX && !pipe.scored) {{
                score++;
                scoreSound.play();
                pipe.scored = true;
            }}
        }});

        if (checkCollision()) {{
            showGameOver();
            return;
        }}

        frame++;
        requestAnimationFrame(gameLoop);
    }}

    // Start game (combined from both codes)
    function startGame() {{
        gameOverScreen.style.display = "none";
        birdY = 250;
        velocity = 0;
        pipes = [];
        frame = 0;
        score = 0;
        currentPipeSpeed = {speed} + 1; // Initialize currentPipeSpeed with a baseline + slider value (e.g., speed 1 becomes 2)
        paused = false;
        ready = false;
        gameRunning = true;
        countdownDiv.style.display = "block"; // From first code

        bgMusic.currentTime = 0; // From first code
        bgMusic.play(); // From first code

        // Initialize clouds (from second code)
        clouds = [];
        for (let i = 0; i < 10; i++) {{
            const x = Math.random() * canvas.width;
            const y = Math.random() * (canvas.height / 2 - cloudSize / 2) + 20;
            clouds.push({{ x: x, y: y }});
        }}

        // Initialize grass layers (from second code)
        grassesForeground = [];
        for (let i = 0; i < 90; i++) {{
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeFG * 0.1));
            const maxGrassY = canvas.height + (grassSizeFG * 0.3);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeFG * 0.05)));
            if (!isOverlappingPipes(x, actualY, grassSizeFG, grassSizeFG)) {{ // Add check for initial grass placement
                grassesForeground.push({{ x: x, y: actualY }});
            }}
        }}

        grassesMidground = [];
        for (let i = 0; i < 60; i++) {{
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeMG * 0.1));
            const maxGrassY = canvas.height + (grassSizeMG * 0.2);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeMG * 0.05)));
            if (!isOverlappingPipes(x, actualY, grassSizeMG, grassSizeMG)) {{ // Add check for initial grass placement
                grassesMidground.push({{ x: x, y: actualY }});
            }}
        }}

        grassesBackground = [];
        for (let i = 0; i < 40; i++) {{
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeBG * 0.05));
            const maxGrassY = canvas.height + (grassSizeBG * 0.1);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeBG * 0.02)));
            if (!isOverlappingPipes(x, actualY, grassSizeBG, grassSizeBG)) {{ // Add check for initial grass placement
                grassesBackground.push({{ x: x, y: actualY }});
            }}
        }}


        let countdown = 3; // From first code
        countdownDiv.innerText = "Ready in " + countdown;
        let interval = setInterval(() => {{
            countdown--;
            if (countdown === 0) {{
                countdownDiv.innerText = "Go!";
                setTimeout(() => {{
                    countdownDiv.style.display = "none";
                    ready = true;
                    gameLoop();
                }}, 500);
                clearInterval(interval);
            }} else {{
                countdownDiv.innerText = "Ready in " + countdown;
            }}
        }}, 1000);
    }}

    loadHighScore();
    drawScore();
    startGame();
    </script>
    """,
    height=720
)




