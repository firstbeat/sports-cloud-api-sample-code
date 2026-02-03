/**
 * Firstbeat Sports Cloud API - JWT Generation Example
 * 
 * Dependencies (Maven coordinates):
 *   - com.auth0:java-jwt:4.4.0 (or newer)
 * 
 * Compile & Run:
 *   javac -cp "path/to/java-jwt.jar" JwtCreate.java
 *   java -cp ".:path/to/java-jwt.jar" JwtCreate <consumer_id> <shared_secret>
 */

import java.util.Calendar;
import java.util.Date;
import com.auth0.jwt.JWT;
import com.auth0.jwt.algorithms.Algorithm;
import com.auth0.jwt.exceptions.JWTCreationException;

public class JwtCreate {

    public static String createJwtToken(String consumerId, String sharedSecret) {
        try {
            // Algorithm is HMAC256
            Algorithm algorithm = Algorithm.HMAC256(sharedSecret);
            
            Calendar c = Calendar.getInstance();
            Date now = c.getTime();
            
            // Expires in 5 minutes (300 seconds)
            c.add(Calendar.SECOND, 300);
            Date expires = c.getTime();

            return JWT.create()
                .withIssuer(consumerId)
                .withIssuedAt(now)
                .withExpiresAt(expires)
                .sign(algorithm);
                
        } catch (IllegalArgumentException e) {
            System.err.println("Error: Shared secret cannot be null or empty.");
            return null;
        } catch (JWTCreationException e) {
            System.err.println("Error creating JWT: " + e.getMessage());
            return null;
        }
    }

    public static void main(String[] args) {
        if (args.length != 2) {
            System.out.println("Usage: java JwtCreate <consumer_id> <shared_secret>");
            System.exit(1);
        }

        String consumerId = args[0];
        String sharedSecret = args[1];

        String token = createJwtToken(consumerId, sharedSecret);
        
        if (token != null) {
            System.out.println("Bearer " + token);
        } else {
            System.exit(1);
        }
    }
}
