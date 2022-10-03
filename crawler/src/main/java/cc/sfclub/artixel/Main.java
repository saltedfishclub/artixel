package cc.sfclub.artixel;

import javax.net.ssl.SSLParameters;
import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicLong;

public class Main {
    private static final String BASE = "https://api.curseforge.com";
    public static AtomicLong lastActive = new AtomicLong(System.currentTimeMillis());
    private final HttpClient client = HttpClient.newBuilder()
            //  .sslParameters(prepareSSLParameter())
            .build();
    private final AtomicInteger counter = new AtomicInteger();

    public static void main(String[] args) {
        new Main().run();
    }

    private SSLParameters prepareSSLParameter() {
        return new SSLParameters();
    }

    private void run() {
        new McModCrawler(client, Path.of("out"))
                .run();
        while (System.currentTimeMillis() - lastActive.get() < 3 * 60 * 1000) { // for 3 minutes
        }
    }

}