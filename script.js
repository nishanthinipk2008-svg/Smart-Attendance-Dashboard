// Load dashboard data when page opens
window.addEventListener("DOMContentLoaded", function () {
    loadStats();
    loadRecords();
});


// -----------------------------
// LOAD DASHBOARD STATISTICS
// -----------------------------

function loadStats() {

    fetch("/api/stats")
        .then(response => response.json())
        .then(data => {

            document.getElementById("totalStudents").innerText =
                data.totalStudents;

            document.getElementById("present").innerText =
                data.present;

            document.getElementById("absent").innerText =
                data.absent;

            document.getElementById("percentage").innerText =
                data.percentage + "%";
        })
        .catch(error => {
            console.error("Error loading statistics:", error);
        });
}


// -----------------------------
// MARK ATTENDANCE
// -----------------------------

function markAttendance() {

    let name = document.getElementById("studentName").value.trim();
    let status = document.getElementById("status").value;

    if (name === "") {
        alert("Please enter student name");
        return;
    }

    fetch("/api/attendance", {

        method: "POST",

        headers: {
            "Content-Type": "application/json"
        },

        body: JSON.stringify({
            student_name: name,
            status: status
        })
    })

    .then(response => response.json())

    .then(data => {

        if (data.error) {
            alert(data.error);
            return;
        }

        alert("Attendance marked successfully!");

        document.getElementById("studentName").value = "";

        // Refresh dashboard
        loadStats();
        loadRecords();
    })

    .catch(error => {
        console.error("Error:", error);
        alert("Something went wrong!");
    });
}


// -----------------------------
// LOAD ATTENDANCE RECORDS
// -----------------------------

function loadRecords() {

    fetch("/api/attendance")

        .then(response => response.json())

        .then(records => {

            let table =
                document.getElementById("attendanceTable");

            // Clear old records
            table.innerHTML = "";

            records.forEach(record => {

                let row = table.insertRow();

                row.insertCell(0).innerText =
                    record.student_name;

                row.insertCell(1).innerText =
                    record.status;

                row.insertCell(2).innerText =
                    record.date;
            });
        })

        .catch(error => {
            console.error("Error loading records:", error);
        });
}