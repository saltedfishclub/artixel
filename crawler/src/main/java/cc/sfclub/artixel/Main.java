package cc.sfclub.artixel;

import java.net.http.HttpClient;
import java.nio.file.Path;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicLong;

public class Main {
    public static AtomicLong lastActive = new AtomicLong(System.currentTimeMillis());
    private final HttpClient client = HttpClient.newBuilder()
            .executor(Executors.newFixedThreadPool(4))
            //  .sslParameters(prepareSSLParameter())
            .build();

    public static void main(String[] args) {
        new Main().run();
    }

    private void run() {
        Path.of("out").toFile().mkdirs();
        new McModCrawler(client, Path.of("out"))
                .run();
        while (System.currentTimeMillis() - lastActive.get() < 3 * 60 * 1000) { // for 3 minutes
        }
    }

}