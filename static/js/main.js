function openTab(event, tabName) {

    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.classList.remove('active'));

    const tabButtons = document.querySelectorAll('.tab-button');
    tabButtons.forEach(button => button.classList.remove('active'));
 document.getElementById(tabName).classList.add('active');
    event.currentTarget.classList.add('active');
}

function register(role) {
    alert(`Registering as ${role}...`);
     switch (role) {
        case 'Patient':
            window.location.href = 'patient_login.html';
            break;
        case 'Doctor':
            window.location.href = 'doctor_login.html';
            break;
        case 'Receptionist':
            window.location.href = 'receptionist_login.html';
            break;
    }
}
