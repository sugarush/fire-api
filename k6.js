import http from 'k6/http';
import { group, sleep, check } from 'k6';

// Get login credentials from env vars
let username = 'administrator';
let password = 'administrator';

export default function() {
    // Login to get API session token
    let res = http.post('http://localhost:8080/v1/authentication',
        JSON.stringify({ data: { username: username, password: password } }),
        { headers: {
          'Content-Type': 'application/vnd.api+json',
          'Accept': 'application/vnd.api+json'
        } }
    );

    let token = res.json().data.token;

    /*res = http.get('http://localhost:8080/v1/users/' + token.id, {
      headers: {
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/vnd.api+json'
      }
    });

    console.log(res.json().data)

    sleep(1);

    // Extract API session token from JSON response
    let apiToken = res.json().token.key;

    // Use session token to make API requests
    res = http.get('https://api.loadimpact.com/v3/account/me',
        { headers: { 'Authorization': 'Token ' + apiToken } }
    );
    check(res, {
        'status is 200': (res) => res.status === 200,
        'content-type is application/json': (res) => res.headers['Content-Type'] === 'application/json',
        'content OK': (res) => JSON.parse(res.body).hasOwnProperty('organizations')
    });

    sleep(3);*/
}
