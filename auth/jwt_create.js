/**
 * Firstbeat Sports Cloud API - JWT Generation Script
 * 
 * Usage:
 *   node jwt_create.js <consumer_id> <shared_secret>
 * 
 * Prerequisites:
 *   npm install jsonwebtoken
 */

const jwt = require('jsonwebtoken');

function createJwtToken(consumerId, sharedSecret) {
    const now = Math.floor(Date.now() / 1000);
    const payload = {
        iss: consumerId,
        iat: now,
        exp: now + 300  // 5 minutes
    };
    
    // Explicitly specify HS256 algorithm
    return jwt.sign(payload, sharedSecret, { algorithm: 'HS256' });
}

function main() {
    const args = process.argv.slice(2);
    
    if (args.length !== 2) {
        console.error("Usage: node jwt_create.js <consumer_id> <shared_secret>");
        process.exit(1);
    }
    
    const [consumerId, sharedSecret] = args;
    
    try {
        const token = createJwtToken(consumerId, sharedSecret);
        console.log(`Bearer ${token}`);
    } catch (error) {
        console.error("Error generating token:", error.message);
        process.exit(1);
    }
}

main();
