// Suits and ranks
const SUITS = ["♠","♥","♦","♣"];
const RANKS = ["A","2","3","4","5","6","7","8","9","10","J","Q","K"];
const PILE_LABELS = ["A","2","3","4","5","6","7","8","9","10","DRAW","J","Q","K"];

let piles = {};
let foundations = {};
let drawPile = [];
let activePile = null;

// Card object
function Card(suit, rank){
    this.suit = suit;
    this.rank = rank;
}

// Initialize game
function initGame(){
    piles = {};
    PILE_LABELS.forEach(l=>piles[l]=[]);

    foundations = {};
    SUITS.forEach(s=>{
        foundations[s+"_up"]=[];
        foundations[s+"_down"]=[];
    });

    let deck = [];
    for(let d=0; d<2; d++){
        SUITS.forEach(s=>{
            RANKS.forEach(r=>deck.push(new Card(s,r)));
        });
    }

    deck = shuffle(deck);
    deal(deck);
    renderPiles();
    renderFoundations();
}

// Shuffle helper
function shuffle(array){
    for(let i=array.length-1;i>0;i--){
        const j=Math.floor(Math.random()*(i+1));
        [array[i],array[j]]=[array[j],array[i]];
    }
    return array;
}

// Deal function based on rules
function deal(deck){
    while(deck.length>0){
        for(let label of PILE_LABELS){
            if(deck.length===0) break;
            let card = deck.shift();
            piles[label].push(card);

            // After 7,10,K -> extra to draw
            if(label==="7"||label==="10"||label==="K") if(deck.length>0) drawPile.push(deck.shift());

            // Ace dealt -> 2 extra
            if(card.rank==="A" && label!=="DRAW") for(let i=0;i<2;i++) if(deck.length>0) drawPile.push(deck.shift());

            // Matching rank -> 1 extra
            if(label!=="DRAW" && card.rank===label) if(deck.length>0) drawPile.push(deck.shift());
        }
    }
}

// Render piles
function renderPiles(){
    const board=document.getElementById("game-board");
    board.innerHTML="";
    PILE_LABELS.forEach(label=>{
        const pileDiv=document.createElement("div");
        pileDiv.className="pile";
        if(label===activePile) pileDiv.classList.add("active-pile");
        pileDiv.id="pile-"+label;
        pileDiv.innerHTML=`<strong>${label}</strong>`;
        piles[label].forEach((card,index)=>{
            const cardDiv=document.createElement("div");
            cardDiv.className="card";
            cardDiv.textContent=card.rank+card.suit;
            cardDiv.dataset.pile=label;
            cardDiv.dataset.index=index;

            if(label===activePile || index===piles[label].length-1){
                cardDiv.draggable=true;
                cardDiv.addEventListener("dragstart",dragStart);
            }
            pileDiv.appendChild(cardDiv);
        });
        pileDiv.addEventListener("dragover",allowDrop);
        pileDiv.addEventListener("drop",dropCard);
        board.appendChild(pileDiv);
    });
}

// Render foundations
function renderFoundations(){
    const container=document.getElementById("foundation-piles");
    container.innerHTML="";
    SUITS.forEach(s=>{
        ["_up","_down"].forEach(dir=>{
            const div=document.createElement("div");
            div.className="foundation";
            const f=foundations[s+dir];
            div.textContent=f.length>0?f[f.length-1].rank+s:dir==="_up"?"A→K":"K→A";
            container.appendChild(div);
        });
    });
}

// Drag-and-drop handlers
let draggedCard=null;
function dragStart(e){
    draggedCard=e.target;
    e.dataTransfer.setData("text/plain","");
    setTimeout(()=>{draggedCard.classList.add("dragging");},0);
}
function allowDrop(e){ e.preventDefault(); }
function dropCard(e){
    e.preventDefault();
    const targetPile=e.currentTarget.id.replace("pile-","");
    if(!draggedCard) return;
    const pileLabel=draggedCard.dataset.pile;
    const index=parseInt(draggedCard.dataset.index);
    const card=piles[pileLabel][index];

    if(canMoveToFoundation(card)){
        moveToFoundation(card);
        piles[pileLabel].splice(index,1);
        renderPiles();
        renderFoundations();
        checkGameEnd();
    }
    draggedCard.classList.remove("dragging");
    draggedCard=null;
}

// Foundation logic
function canMoveToFoundation(card){
    const up=foundations[card.suit+"_up"];
    const down=foundations[card.suit+"_down"];
    if(up.length===0 && card.rank==="A") return true;
    if(up.length>0 && nextRank(up[up.length-1].rank)===card.rank) return true;
    if(down.length===0 && card.rank==="K") return true;
    if(down.length>0 && prevRank(down[down.length-1].rank)===card.rank) return true;
    return false;
}
function moveToFoundation(card){
    const up=foundations[card.suit+"_up"];
    const down=foundations[card.suit+"_down"];
    if(up.length===0 && card.rank==="A") up.push(card);
    else if(up.length>0 && nextRank(up[up.length-1].rank)===card.rank) up.push(card);
    else if(down.length===0 && card.rank==="K") down.push(card);
    else down.push(card);
}
function nextRank(r){ return RANKS[RANKS.indexOf(r)+1]; }
function prevRank(r){ return RANKS[RANKS.indexOf(r)-1]; }

// Draw button
document.getElementById("draw-button").addEventListener("click",()=>{
    if(drawPile.length===0){
        alert("DRAW pile is empty!");
        checkGameEnd();
        return;
    }
    const card=drawPile.pop();
    activePile=card.rank;
    piles[activePile].push(card);
    renderPiles();
});

// Check for game end
function checkGameEnd(){
    const allComplete=SUITS.every(s=>{
        return foundations[s+"_up"].length===13 && foundations[s+"_down"].length===13;
    });
    const noMovesLeft=Object.keys(piles).every(label=>{
        return piles[label].every(card=>!canMoveToFoundation(card));
    });
    if(allComplete){
        alert("Congratulations! You have won by completing all foundations!");
    } else if(noMovesLeft && drawPile.length===0){
        alert("Game over! No valid moves left and draw pile is empty.");
    }
}

// Start game
initGame();
