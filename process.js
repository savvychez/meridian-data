const { spawn } = require('child_process');
const { finished } = require('stream');
const prompt = require('prompt-sync')();

var start = console.time('Execution Time')

var dateRange = (start, end) => {
    var dates = []
    var currentDate = start
    function addDays(days) {
        var date = new Date(this.valueOf());
        date.setDate(date.getDate() + days);
        return date;
    };
    while (currentDate <= end) {
        dates.push(currentDate);
        currentDate = addDays.call(currentDate, 1);
    }
    return dates;
};

const finish = (single, dates) => {
    if (single === true) {
        console.log("Processed!")
    } else {
        console.log(`Finished processing dates from ${dates[0].toISOString().split('T')[0].replaceAll('-', '/')} to ${dates[dates.length - 1].toISOString().split('T')[0].replaceAll('-', '/')}!`)
    }
    console.timeEnd('Execution Time')
}

const processDate = (date, single) => {
    formattedDate = date.toISOString().split('T')[0].replaceAll('-', '/')
    console.log(`Processing data for ${formattedDate}...`);
    const python = spawn('python', ['export.py', formattedDate]);
    python.on('exit', function () {
        if (!single) {
            s += 1
            if (s < e)
                processDate(dates[s])
            else
                finish(false, dates)
        }
        else
            finish(true)
    })
}


console.log("\n--Meridian Date Processor--")
let args = process.argv.slice(2);
let single = false
if (args.length == 1) {
    start = args[0]
    single = true
}
else if (args.length == 2) {
    start = args[0]
    end = args[1]
} else {
    console.log("No command line arguments provided! Deferring to user input...\n")
    start = prompt("Start Date (YYYY/MM/DD): ")
    end = prompt("End Date (YYYY/MM/DD): ")
}

let dates = dateRange(new Date(start), new Date(end));
let s = 0
let e = dates.length

if (single === true) {
    let date = new Date(start)
    processDate(date, single)
} else {
    console.log(`Processing OISST data from ${start} to ${end}`)

    processDate(dates[s])
}


