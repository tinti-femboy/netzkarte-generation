
/**
 *  Close the legend a short time after the map loads
 */ 
setTimeout(() => {
    legend.classList.toggle('open');
    // Play CSS animation "glowing"
    btn.classList.add('glowing');
}, 500);


/**
 *  Toggle legend visibility 
 */ 
const legend = document.getElementById('legend');
const btn = document.getElementById('toggle-btn');

btn.addEventListener('click', () => {
    legend.classList.toggle('open');
});


