
let seconds = 0;
let minutes = 0;
let hours = 0;
let timer = null;

function startTimer() {

    if (timer !== null) {
        return;
    }

    timer = setInterval(function () {

        seconds++;

        if (seconds == 60) {
            seconds = 0;
            minutes++;
        }

        if (minutes == 60) {
            minutes = 0;
            hours++;
        }

        document.getElementById("timer").innerHTML =
            hours + "h " + minutes + "m " + seconds + "s";

    }, 1000);
}

function stopTimer() {

    clearInterval(timer);
    timer = null;

    // convert timer to hours
    let totalHours = hours + (minutes / 60) + (seconds / 3600);

    // put value in input box
    document.getElementById("hoursInput").value = totalHours.toFixed(2);
}