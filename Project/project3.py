import streamlit as st
import streamlit.components.v1 as components


st.set_page_config(page_title="Flappy Runner", layout="centered")
st.title("🏃‍➡️ Flappy Runner - Streamlit Edition")


components.html(
    """
    <style>
    body {
        overflow: hidden;
    }
    canvas {
        border: 2px solid black;
        /* Background handled by JS gradients */
    }
    #gameOverScreen {
        display: none;
        text-align: center;
        position: absolute;
        top: 200px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0, 0, 0, 0.75);
        color: white;
        padding: 20px;
        border-radius: 10px;
        z-index: 20; /* Ensure it's above everything */
    }
    #scoreDisplay {
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
    }
    /* Import Google Font for the score */
    @import url('https://fonts.googleapis.com/css2?family=Press+Start+2P&display=swap');
    </style>


    <canvas id="gameCanvas" width="400" height="600"></canvas>
    <div id="gameOverScreen">
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


    const birdEmote = "🕊️"; // Single bird emote


    let pipes = [];
    const pipeWidth = 50;
    const pipeGap = 150;
    let frame = 0;
    let score = 0;
    let highScore = 0;
    let gameRunning = false;


    // Variables for clouds
    let clouds = [];
    const cloudEmote = "☁️";
    const cloudSize = 40; // Base size for clouds
    const cloudMinSize = 25; // Minimum cloud size
    const cloudMaxSize = 60; // Maximum cloud size


    // New variables for multiple grass layers and ground
    let grassesForeground = [];
    const grassEmoteFG = "🌿";
    const grassSizeFG = 45; // Base size for foreground grass


    let grassesMidground = [];
    const grassEmoteMG = "🌱";
    const grassSizeMG = 35; // Base size for midground grass


    let grassesBackground = [];
    const grassEmoteBG = "🍃";
    const grassSizeBG = 25; // Base size for background grass


    const groundHeight = 100; // Height of the solid ground block




    const gameOverScreen = document.getElementById("gameOverScreen");
    const finalScoreText = document.getElementById("finalScoreText");
    const highScoreText = document.getElementById("highScoreText");
    const scoreDisplay = document.getElementById("scoreDisplay");


    window.addEventListener("keydown", function(e) {
        if (["ArrowUp"].includes(e.key)) e.preventDefault();
    }, false);


    document.addEventListener("keydown", function(e) {
        if (e.key === "ArrowUp" && gameRunning) {
            velocity = flapStrength;
        }
    });


    function drawBird() {
        ctx.font = `${birdSize}px serif`;
        ctx.save(); // Save the current canvas state


        ctx.translate(birdX + birdSize / 2, birdY);
        ctx.scale(-1, 1); // Flip horizontally


        ctx.fillText(birdEmote, -(birdSize / 2), birdSize / 4);


        ctx.restore(); // Restore the canvas to its original state
    }


    // Function to draw the background (sky and ground gradients)
    function drawBackground() {
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
    }


    // Enhanced drawPipes for shading
    function drawPipes() {
        ctx.shadowColor = 'rgba(0, 0, 0, 0.5)'; // Add a subtle shadow to pipes
        ctx.shadowBlur = 5;
        ctx.shadowOffsetX = 3;
        ctx.shadowOffsetY = 3;


        pipes.forEach(pipe => {
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
            ctx.fillRect(pipe.x, pipe.top + pipeGap, pipeWidth, 5);
        });
        ctx.shadowBlur = 0; // Reset shadow for other elements
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
    }


    function updatePipes() {
        if (frame % 100 === 0) {
            const minTop = 50;
            const maxTop = canvas.height - pipeGap - groundHeight - 50;
            if (maxTop < minTop) {
                console.warn("Canvas height is too small for pipe generation with current constraints!");
                const adjustedMaxTop = minTop + 20;
                const top = Math.random() * (adjustedMaxTop - minTop) + minTop;
                pipes.push({ x: canvas.width, top: top });
            } else {
                const top = Math.random() * (maxTop - minTop) + minTop;
                pipes.push({ x: canvas.width, top: top });
            }
        }


        pipes.forEach(pipe => pipe.x -= 2);
        pipes = pipes.filter(pipe => pipe.x + pipeWidth > 0);
    }


    // Helper function to check for overlap with pipes
    function isOverlappingPipes(grassX, grassY, grassWidth, grassHeight) {
        for (let pipe of pipes) {
            // Check horizontal overlap with pipe
            if (grassX < pipe.x + pipeWidth && grassX + grassWidth > pipe.x) {
                // If horizontally overlapping, check if vertically within the pipe's upper or lower section (or gap)
                // grassY is the baseline, so its top is roughly grassY - grassHeight (for square bounding box)
                const grassTop = grassY - grassHeight;
                const grassBottom = grassY;


                // Check if any part of the grass emote overlaps with the upper pipe, the gap, or the lower pipe
                // This means the grass's vertical range should NOT be within the pipe's vertical range
                const pipeTopEdge = 0; // Top of upper pipe
                const pipeBottomEdge = canvas.height; // Bottom of lower pipe (canvas height)


                // If grass is within the vertical bounds of either pipe or the gap, it overlaps
                if (
                    (grassBottom > pipeTopEdge && grassTop < pipe.top) || // Overlaps with upper pipe body
                    (grassBottom > pipe.top + pipeGap && grassTop < pipeBottomEdge) || // Overlaps with lower pipe body
                    (grassBottom > pipe.top && grassTop < pipe.top + pipeGap) // Overlaps with the gap itself
                ) {
                    return true;
                }
            }
        }
        return false;
    }




    // Functions for clouds (updated for more density and random initial x AND dynamic sizing)
    function drawClouds() {
        clouds.forEach(cloud => {
            const relativeY = cloud.y;
            const skyHeight = canvas.height - groundHeight;
            const scaleFactor = 0.5 + (relativeY / skyHeight * 0.5);
            const currentCloudSize = Math.max(cloudMinSize, Math.min(cloudMaxSize, cloudSize * scaleFactor));


            ctx.font = `${currentCloudSize}px serif`;
            ctx.fillText(cloudEmote, cloud.x, cloud.y);
        });
    }


    function updateClouds() {
        if (frame % 70 === 0) {
            const x = canvas.width + Math.random() * 100;
            const y = Math.random() * (canvas.height / 2 - cloudSize / 2) + 20;
            clouds.push({ x: x, y: y });
        }
        clouds.forEach(cloud => cloud.x -= 0.5);
        clouds = clouds.filter(cloud => cloud.x + cloudMaxSize > 0);
    }


    // Functions for Foreground Grass
    function drawGrassesForeground() {
        grassesForeground.forEach(grass => {
            const relativeY = grass.y - (canvas.height - groundHeight);
            const adjustedScale = 0.5 + (relativeY / (groundHeight * 1.5));
            const finalScale = Math.max(0.5, Math.min(1.2, adjustedScale));
            const currentSize = grassSizeFG * finalScale;
            ctx.font = `${currentSize}px serif`;
            ctx.fillText(grassEmoteFG, grass.x, grass.y);
        });
    }


    function updateGrassesForeground() {
        if (frame % 5 === 0) {
            const x = canvas.width + Math.random() * 20;
            const minGrassY = (canvas.height - groundHeight + (grassSizeFG * 0.1));
            const maxGrassY = canvas.height + (grassSizeFG * 0.3);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeFG * 0.05)));


            if (!isOverlappingPipes(x, actualY, grassSizeFG, grassSizeFG)) {
                grassesForeground.push({ x: x, y: actualY });
            }
        }
        grassesForeground.forEach(grass => grass.x -= 2);
        grassesForeground = grassesForeground.filter(grass => grass.x > -grassSizeFG);
    }


    // Functions for Midground Grass
    function drawGrassesMidground() {
        grassesMidground.forEach(grass => {
            const relativeY = grass.y - (canvas.height - groundHeight);
            const adjustedScale = 0.5 + (relativeY / (groundHeight * 1.5));
            const finalScale = Math.max(0.5, Math.min(1.2, adjustedScale));
            const currentSize = grassSizeMG * finalScale;
            ctx.font = `${currentSize}px serif`;
            ctx.fillText(grassEmoteMG, grass.x, grass.y);
        });
    }


    function updateGrassesMidground() {
        if (frame % 10 === 0) {
            const x = canvas.width + Math.random() * 30;
            const minGrassY = (canvas.height - groundHeight + (grassSizeMG * 0.1));
            const maxGrassY = canvas.height + (grassSizeMG * 0.2);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeMG * 0.05)));


            if (!isOverlappingPipes(x, actualY, grassSizeMG, grassSizeMG)) {
                grassesMidground.push({ x: x, y: actualY });
            }
        }
        grassesMidground.forEach(grass => grass.x -= 2);
        grassesMidground = grassesMidground.filter(grass => grass.x > -grassSizeMG);
    }


    // Functions for Background Grass/Foliage
    function drawGrassesBackground() {
        grassesBackground.forEach(grass => {
            const relativeY = grass.y - (canvas.height - groundHeight);
            const adjustedScale = 0.5 + (relativeY / (groundHeight * 1.5));
            const finalScale = Math.max(0.5, Math.min(1.2, adjustedScale));
            const currentSize = grassSizeBG * finalScale;
            ctx.font = `${currentSize}px serif`;
            ctx.fillText(grassEmoteBG, grass.x, grass.y);
        });
    }


    function updateGrassesBackground() {
        if (frame % 20 === 0) {
            const x = canvas.width + Math.random() * 40;
            const minGrassY = (canvas.height - groundHeight + (grassSizeBG * 0.05));
            const maxGrassY = canvas.height + (grassSizeBG * 0.1);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeBG * 0.02)));


            if (!isOverlappingPipes(x, actualY, grassSizeBG, grassSizeBG)) {
                grassesBackground.push({ x: x, y: actualY });
            }
        }
        grassesBackground.forEach(grass => grass.x -= 2);
        grassesBackground = grassesBackground.filter(grass => grass.x > -grassSizeBG);
    }


    function checkCollision() {
        for (let pipe of pipes) {
            if (birdX + birdSize > pipe.x && birdX < pipe.x + pipeWidth) {
                if (birdY < pipe.top || birdY + birdSize > pipe.top + pipeGap) return true;
            }
        }
        if (birdY + birdSize > canvas.height - groundHeight) return true;
        return birdY < 0;
    }


    function drawScore() {
        scoreDisplay.innerText = `Score: ${score} | 🏆 High: ${highScore}`;
    }


    function showGameOver() {
        gameRunning = false;
        gameOverScreen.style.display = "block";
        finalScoreText.textContent = "You scored " + score + " points!";
        if (score > highScore) highScore = score;
        highScoreText.textContent = "High Score: " + highScore;
    }


    function gameLoop() {
        if (!gameRunning) return;


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


        drawScore();


        velocity += gravity;
        birdY += velocity;


        if (frame % 100 === 0) score++;


        if (checkCollision()) {
            showGameOver();
            return;
        }


        frame++;
        requestAnimationFrame(gameLoop);
    }


    function startGame() {
        gameOverScreen.style.display = "none";
        birdY = 250;
        velocity = 0;
        pipes = [];
        frame = 0;
        score = 0;
        gameRunning = true;


        clouds = [];
        for (let i = 0; i < 10; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * (canvas.height / 2 - cloudSize / 2) + 20;
            clouds.push({ x: x, y: y });
        }


        grassesForeground = [];
        for (let i = 0; i < 90; i++) {
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeFG * 0.1));
            const maxGrassY = canvas.height + (grassSizeFG * 0.3);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeFG * 0.05)));
            grassesForeground.push({ x: x, y: actualY });
        }


        grassesMidground = [];
        for (let i = 0; i < 60; i++) {
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeMG * 0.1));
            const maxGrassY = canvas.height + (grassSizeMG * 0.2);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeMG * 0.05)));
            grassesMidground.push({ x: x, y: actualY });
        }


        grassesBackground = [];
        for (let i = 0; i < 40; i++) {
            const x = Math.random() * canvas.width;
            const minGrassY = (canvas.height - groundHeight + (grassSizeBG * 0.05));
            const maxGrassY = canvas.height + (grassSizeBG * 0.1);
            const y = minGrassY + Math.random() * (maxGrassY - minGrassY);
            const actualY = Math.max(y, (canvas.height - groundHeight + (grassSizeBG * 0.02)));
            grassesBackground.push({ x: x, y: actualY });
        }


        gameLoop();
    }


    startGame();
    </script>
    """,
    height=700
)

