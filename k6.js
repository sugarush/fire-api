import http from 'k6/http';
import { group, sleep, check } from 'k6';

// Get login credentials from env vars
let username = 'administrator';
let password = 'administrator';

export default function() {
    let res = http.get('http://localhost:8080/v1/users', {
      headers: {
        'Content-Type': 'application/vnd.api+json',
        'Accept': 'application/vnd.api+json'
      }
    });


    check(res, {
      'status is 200': (res) => res.status === 200,
      'content-type is application/vnd.api+json': (res) => {
        return res.headers['Content-Type'] === 'application/vnd.api+json'
      },
      'content ok': (res) => {
        return JSON.parse(res.body).hasOwnProperty('data');
      }
    });
}
