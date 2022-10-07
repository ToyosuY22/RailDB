// Password Check
const pwd1 = document.getElementById('id_old_password');
const pwdCheck1 = document.getElementById('old-password-check');
pwdCheck1.addEventListener('change', function () {
    if (pwdCheck1.checked) {
        pwd1.setAttribute('type', 'text');
    } else {
        pwd1.setAttribute('type', 'password');
    }
}, false);

const pwd2 = document.getElementById('id_new_password');
const pwdCheck2 = document.getElementById('new-password-check');
pwdCheck2.addEventListener('change', function () {
    if (pwdCheck2.checked) {
        pwd2.setAttribute('type', 'text');
    } else {
        pwd2.setAttribute('type', 'password');
    }
}, false);
