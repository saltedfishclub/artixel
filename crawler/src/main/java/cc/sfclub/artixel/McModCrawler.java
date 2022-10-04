package cc.sfclub.artixel;

import lombok.SneakyThrows;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.ThreadLocalRandom;
import java.util.concurrent.TimeUnit;
import java.util.regex.Pattern;

public class McModCrawler extends AbstractCrawler {
    private static final Pattern PATTERN_EXTRACT_ID = Pattern.compile("href=\"\\/item\\/(\\d+)\\.html\"");
    private static final Pattern ENGLISH_NAME = Pattern.compile("<span class=\"name\" data-id=\"0\"><h5>(.*?)<\\/h5><\\/span>");
    private static final Pattern IMAGE = Pattern.compile("(i\\.mcmod\\.cn\\/item\\/icon\\/(.+)\\/\\d+\\/\\d+\\.png)");

    private static final Pattern COMMON_ASCII = Pattern.compile("^[a-zA-Z0-9-' ]+");
    private static final Pattern QUOTE = Pattern.compile("\\((.+)\\)");
    private final HttpClient client;
    private final Path storage;

    public McModCrawler(HttpClient client, Path pathToStore) {
        super("https://www.mcmod.cn");
        this.client = client;
        storage = pathToStore;
    }

    @SneakyThrows
    @Override
    public void run() {
        for (int i = 1; i < 7768; i++) {
            // https://www.mcmod.cn/item/list/2-1.html
            Main.lastActive.set(System.currentTimeMillis());
            var req = withHeader("/item/list/" + i + "-1.html")
                    .GET().build();
            int finalI = i;
            client.sendAsync(req, HttpResponse.BodyHandlers.ofString())
                    .thenAccept(resp -> parseResp(resp, finalI));
            Thread.sleep(ThreadLocalRandom.current().nextInt(1000, 3000));
        }
    }


    @SneakyThrows
    private void parseResp(HttpResponse<String> resp, int i) {
        Main.lastActive.set(System.currentTimeMillis());
        if (resp.statusCode() != 200) {
            System.out.println("Status Code is not 200 when requesting " + i + " :" + resp.statusCode());
        }
        var body = resp.body();
        var matcher = PATTERN_EXTRACT_ID.matcher(body);
        while (matcher.find()) {
            var id = matcher.group(1);
            if (Files.exists(storage.resolve(id + ".jpg"))) {
                System.out.println("Already found: " + id);
                continue;
            }
            // i.mcmod.cn/item/icon/32x32/19/191087.png?v=1
            Thread.sleep(ThreadLocalRandom.current().nextInt(3000, 6000));
            var payload = withHeader("/item/" + id + ".html").GET().build();
            client.sendAsync(payload, HttpResponse.BodyHandlers.ofString())
                    .thenAccept(r -> readInfo(r, 0, Integer.parseInt(id)));
        }
        //System.out.println(body);
    }

    @SneakyThrows
    private void readInfo(HttpResponse<String> resp, int retries, int id) {
        Main.lastActive.set(System.currentTimeMillis());
        if (resp.statusCode() != 200) {
            System.err.println("Not 200! re-trying... " + retries + " statusCode: " + resp.statusCode());
            SCHEDULER.scheduleWithFixedDelay(() -> {
                var payload = withHeader("/item/" + id + ".html").GET().build();
                client.sendAsync(payload, HttpResponse.BodyHandlers.ofString())
                        .thenAccept(r -> readInfo(r, retries + 1, id));
            }, 0L, 15L, TimeUnit.SECONDS);
            return;
        }
        var body = resp.body();
        var matcher = ENGLISH_NAME.matcher(body);

        String engName;
        if (matcher.find()) {
            // english name!
            engName = matcher.group(1);
            if (!COMMON_ASCII.matcher(engName).matches()) {
                // 氧化的铜块 (Oxidized Copper)
                var m2 = QUOTE.matcher(engName);
                if (!m2.find()) {
                    System.err.println("Cannot find name for " + id + " : " + engName);
                    return;
                }
                engName = m2.group(1);
            }
        } else {
            System.err.println("Cannot find name for " + id);
            return;
        }

        matcher = IMAGE.matcher(body);
        if (!matcher.find()) {
            System.err.println("Cannot find image for " + id);
            return;
        }
        var resolution = matcher.group(2);
        // download

        var payload = withHeader("").GET().uri(URI.create("https://" + matcher.group(1).replaceAll(resolution, "32x32"))).build();
        Thread.sleep(ThreadLocalRandom.current().nextInt(1000, 3000));
        System.out.println("Start downloading: " + id);
        client.sendAsync(payload, HttpResponse.BodyHandlers.ofFile(storage.resolve(id + ".png")));
        Files.writeString(storage.resolve(id + ".txt"), engName);

    }
}
