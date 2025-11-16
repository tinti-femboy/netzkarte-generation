export function signalIconPath(reception) {
    if(reception == 1){
        console.log(reception)
        return("images/signalIcon/0.svg")
    } else if(reception < 10) {
        return("images/signalIcon/25.svg")
    } else if(reception < 20) {
        return("images/signalIcon/50.svg")
    } else if(reception < 50) {
        return("images/signalIcon/75.svg")
    } else {
        return("images/signalIcon/100.svg")
    }
};