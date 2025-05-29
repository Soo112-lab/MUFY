import streamlit as st
import streamlit.components.v1 as components

# Streamlit UI
st.set_page_config(page_title="Flappy Runner", layout="centered")
st.title("🏃‍➡️ I'm Bird-rotting it")


# --- Removed Speed and Difficulty Sliders as per request ---
# The game's speed and pipe gap will now adjust automatically with score.


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
        z-index: 20;
    }}
    #scoreDisplay {{
        position: absolute;
        bottom: 10px;
        left: 50%;
        transform: translateX(-50%);
        font-family: 'Press Start 2P', cursive;
        font-size: 20px;
        font-weight: bold;
        color: #FFF;
        background: rgba(0, 0, 0, 0.6);
        padding: 8px 20px;
        border-radius: 8px;
        border: 2px solid #FFD700;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.8);
        box-shadow: 0px 0px 15px rgba(255, 215, 0, 0.5);
        z-index: 10;
    }}
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


    const birdEmote = "🕊️";


    let pipes = [];
    const pipeWidth = 70;
   
    // --- Dynamic Pipe Gap and Speed Variables ---
    let gameSpeed = 1; // Starts at speed 1
    let currentPipeGap = 200; // Initial "easy" pipe gap (was 180+60=240 for easy, 130+60=190 for medium)


    let frame = 0;
    let score = 0;
    let highScore = 0;
    let gameRunning = false;
    let paused = false;
    let ready = false;


    // This constant will be ignored as gameSpeed now ramps up
    const speedIncreaseRate = 0.0005;


    let clouds = [];
    const cloudEmote = "☁️";
    const cloudSize = 40;
    const cloudMinSize = 25;
    const cloudMaxSize = 60;


    let grassesForeground = [];
    const grassEmoteFG = "🌿";
    const grassSizeFG = 45;


    let grassesMidground = [];
    const grassEmoteMG = "🌱";
    const grassSizeMG = 35;


    let grassesBackground = [];
    const grassEmoteBG = "🍃";
    const grassSizeBG = 25;


    const groundHeight = 100;


    const gameOverScreen = document.getElementById("gameOverScreen");
    const finalScoreText = document.getElementById("finalScoreText");
    const highScoreText = document.getElementById("highScoreText");
    const scoreDisplay = document.getElementById("scoreDisplay");
    const countdownDiv = document.getElementById("countdown");


    const jumpSound = new Audio("https://actions.google.com/sounds/v1/cartoon/wood_plank_flicks.ogg");
    const scoreSound = new Audio('https://audio.jukehost.co.uk/MvoNNWrjBKFfMnyOBYiGU54EWAJiC3gm');
    const gameOverSound = new Audio('https://audio.jukehost.co.uk/0QTMOfboi9npdAqvnssGZFrsi6GTOnlg');
    const bgMusic = new Audio("https://audio.jukehost.co.uk/8LnIiGnXtdZCrfq8jkEJBrDWyQ12ZxyO");
    bgMusic.loop = true;


    window.addEventListener("keydown", function(e) {{
        if (["ArrowUp", " ", "w", "W"].includes(e.key)) {{
            e.preventDefault();
        }}
    }}, false);


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


    document.addEventListener("touchstart", function(e) {{
        e.preventDefault();
        if (gameRunning && !paused && ready) {{
            velocity = flapStrength;
            jumpSound.play();
        }}
    }}, {{ passive: false }});


    function drawBird() {{
        ctx.font = `${{birdSize}}px serif`;
        ctx.save();
        ctx.translate(birdX + birdSize / 2, birdY);
        ctx.scale(-1, 1);
        ctx.fillText(birdEmote, -(birdSize / 2), birdSize / 4);
        ctx.restore();
    }}


    function drawBackground() {{
        const skyGradient = ctx.createLinearGradient(0, 0, 0, canvas.height - groundHeight);
        skyGradient.addColorStop(0, "#6A5ACD");
        skyGradient.addColorStop(1, "#87CEEB");
        ctx.fillStyle = skyGradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height - groundHeight);


        const groundGradient = ctx.createLinearGradient(0, canvas.height - groundHeight, 0, canvas.height);
        groundGradient.addColorStop(0, "#6B8E23");
        groundGradient.addColorStop(1, "#2E8B57");
        ctx.fillStyle = groundGradient;
        ctx.fillRect(0, canvas.height - groundHeight, canvas.width, groundHeight);
    }}


    function drawPipes() {{
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)';
        ctx.shadowBlur = 5;
        ctx.shadowOffsetX = 3;
        ctx.shadowOffsetY = 3;


        pipes.forEach(pipe => {{
            ctx.fillStyle = "#228B22";
            ctx.fillRect(pipe.x, 0, pipeWidth, pipe.top);
            ctx.fillRect(pipe.x, pipe.top + currentPipeGap, pipeWidth, canvas.height - pipe.top - currentPipeGap);


            ctx.fillStyle = "#3CB371";
            ctx.fillRect(pipe.x, 0, pipeWidth / 4, pipe.top);
            ctx.fillRect(pipe.x, pipe.top + currentPipeGap, pipeWidth / 4, canvas.height - pipe.top - currentPipeGap);


            ctx.fillStyle = "#006400";
            ctx.fillRect(pipe.x + pipeWidth * 0.75, 0, pipeWidth / 4, pipe.top);
            ctx.fillRect(pipe.x + pipeWidth * 0.75, pipe.top + currentPipeGap, pipeWidth / 4, canvas.height - pipe.top - currentPipeGap);


            ctx.fillStyle = "#90EE90";
            ctx.fillRect(pipe.x, pipe.top - 5, pipeWidth, 5);
            ctx.fillRect(pipe.x, pipe.top + currentPipeGap - 5, pipeWidth, 5);
        }});
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
    }}


    function updatePipes() {{
        if (pipes.length === 0 || (canvas.width - pipes[pipes.length - 1].x) >= 250) {{
            const minTop = 50;
            const maxTop = canvas.height - currentPipeGap - groundHeight - 50;
            if (maxTop < minTop) {{
                const adjustedMaxTop = minTop + 20;
                const top = Math.random() * (adjustedMaxTop - minTop) + minTop;
                pipes.push({{ x: canvas.width, top: top, scored: false }});
            }} else {{
                const top = Math.random() * (maxTop - minTop) + minTop;
                pipes.push({{ x: canvas.width, top: top, scored: false }});
            }}
        }}


        pipes.forEach(pipe => pipe.x -= gameSpeed);
        pipes = pipes.filter(pipe => pipe.x + pipeWidth > 0);
    }}


    function isOverlappingPipes(entityX, entityY, entityWidth, entityHeight) {{
        for (let pipe of pipes) {{
            if (entityX < pipe.x + pipeWidth && entityX + entityWidth > pipe.x) {{
                const entityTop = entityY - entityHeight;
                const entityBottom = entityY;


                const pipeTopEdge = 0;
                const pipeBottomEdge = canvas.height;


                if (
                    (entityBottom > pipeTopEdge && entityTop < pipe.top) ||
                    (entityBottom > pipe.top + currentPipeGap && entityTop < pipeBottomEdge)
                ) {{
                    return true;
                }}
            }}
        }}
        return false;
    }}


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
        clouds.forEach(cloud => cloud.x -= 0.5); // Very slow for distant clouds
        clouds = clouds.filter(cloud => cloud.x + cloudMaxSize > 0);
    }}


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
        // --- Parallax Adjustment: Faster than main game speed ---
        grassesForeground.forEach(grass => grass.x -= (gameSpeed * 1.1));
        grassesForeground = grassesForeground.filter(grass => grass.x > -grassSizeFG);
    }}


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
        // --- Parallax Adjustment: Same speed as main game elements (pipes) ---
        grassesMidground.forEach(grass => grass.x -= gameSpeed);
        grassesMidground = grassesMidground.filter(grass => grass.x > -grassSizeMG);
    }}


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
        // --- Parallax Adjustment: Slower than main game speed for background ground parallax ---
        grassesBackground.forEach(grass => grass.x -= (gameSpeed * 0.6));
        grassesBackground = grassesBackground.filter(grass => grass.x > -grassSizeBG);
    }}


    const hitboxOffsetX = 0;
    const hitboxOffsetY = -10;
    const hitboxWidth = birdSize - 16;
    const hitboxHeight = birdSize - 15;


    function checkCollision() {{
        for (let pipe of pipes) {{
            if (
                birdX + hitboxOffsetX + hitboxWidth > pipe.x &&
                birdX + hitboxOffsetX < pipe.x + pipeWidth
            ) {{
                if (
                    birdY + hitboxOffsetY < pipe.top ||
                    birdY + hitboxOffsetY + hitboxHeight > pipe.top + currentPipeGap
                ) return true;
            }}
        }}
        if (birdY + birdSize > canvas.height - groundHeight) return true;
        return birdY < 0;
    }}


    function drawScore() {{
        scoreDisplay.innerText = `Score: ${{score}} | 🏆 High: ${{highScore}} | Speed: ${{gameSpeed}}`;
    }}


    function showGameOver() {{
        gameRunning = false;
        gameOverSound.play();
        gameOverScreen.style.display = "block";
        finalScoreText.textContent = "You scored " + score + " points!";
        if (score > highScore) {{
            highScore = score;
            localStorage.setItem("flappyRunnerHighScore", highScore);
        }}
        highScoreText.textContent = "High Score: " + highScore;
        bgMusic.pause();
    }}


    function loadHighScore() {{
        const storedHighScore = localStorage.getItem("flappyRunnerHighScore");
        if (storedHighScore) {{
            highScore = parseInt(storedHighScore);
        }}
    }}


    // --- New Difficulty Ramp-up Function ---
    function updateDifficulty() {{
        // Calculate new speed level based on score (1 speed level per 5 points)
        const newSpeedLevel = Math.floor(score / 5) + 1;
       
        // Ensure speed doesn't decrease and only increases when a threshold is crossed
        if (newSpeedLevel > gameSpeed) {{
            gameSpeed = newSpeedLevel;
            // Optionally, reduce pipe gap as speed increases to make it harder
            // Example: reduce by 5 pixels for every speed level increase, minimum gap of 100
            currentPipeGap = Math.max(100, currentPipeGap - 5);
        }}
    }}


    function gameLoop() {{
        if (!gameRunning || paused || !ready) return;


        ctx.clearRect(0, 0, canvas.width, canvas.height);


        // --- Update Difficulty at the start of each loop ---
        updateDifficulty();


        drawBackground();


        updateClouds();
        drawClouds();
        updateGrassesBackground();
        drawGrassesBackground();


        updatePipes();
        drawPipes();
        updateGrassesMidground();
        drawGrassesMidground();


        drawBird();


        updateGrassesForeground();
        drawGrassesForeground();


        drawScore(); // Score display now includes current game speed


        velocity += gravity;
        birdY += velocity;


        // --- Removed speedIncreaseRate, as speed is now score-driven ---
        // gameSpeed += speedIncreaseRate;


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


    function startGame() {{
        gameOverScreen.style.display = "none";
        birdY = 250;
        velocity = 0;
        pipes = [];
        frame = 0;
        score = 0;
        // --- Reset speed and pipe gap for new game ---
        gameSpeed = 1;
        currentPipeGap = 200;
        paused = false;
        ready = false;
        gameRunning = true;
        countdownDiv.style.display = "block";


        bgMusic.currentTime = 0;
        bgMusic.play();


        clouds = [];
        for (let i = 0; i < 10; i++) {{
            const x = Math.random() * canvas.width;
            const y = Math.random() * (canvas.height / 2 - cloudSize / 2) + 20;
            clouds.push({{ x: x, y: y }});
        }}


        grassesForeground = [];
        for (let i = 0; i < 90; i++) {{
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeFG * 0.1));
            const maxGrassY = canvas.height + (grassSizeFG * 0.3);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeFG * 0.05)));
            grassesForeground.push({{ x: x, y: actualY }});
        }}


        grassesMidground = [];
        for (let i = 0; i < 60; i++) {{
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeMG * 0.1));
            const maxGrassY = canvas.height + (grassSizeMG * 0.2);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeMG * 0.05)));
            grassesMidground.push({{ x: x, y: actualY }});
        }}


        grassesBackground = [];
        for (let i = 0; i < 40; i++) {{
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeBG * 0.05));
            const maxGrassY = canvas.height + (grassSizeBG * 0.1);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeBG * 0.02)));
            grassesBackground.push({{ x: x, y: actualY }});
        }}


        let countdown = 3;
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
    drawBackground();
    drawClouds();
    drawGrassesBackground();
    drawPipes(); // Draw with initial pipe gap
    drawGrassesMidground();
    drawBird();
    drawGrassesForeground();
   
    startGame();
    </script>
    """,
    height=600
)




