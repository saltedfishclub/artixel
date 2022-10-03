package cc.sfclub.artixel;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;

import java.net.http.HttpClient;
import java.net.http.HttpResponse;
import java.util.concurrent.TimeUnit;
import java.util.function.IntConsumer;
import java.util.regex.Pattern;

/**
 * A crawler that keep downloading modlists from server.
 */
@Slf4j
public class ModCrawler extends AbstractCrawler {
    private static final Pattern MATCH_MOD_LNK = Pattern.compile("<a class=\"my-auto\" href=\"(.+)\">");
    private static final Pattern MODID_MATCH = Pattern.compile("Project ID.+\\n<span>(\\d+)</span>");
    private final IntConsumer modidConsumer;
    private volatile boolean ended;

    public ModCrawler(IntConsumer modidConsumer) {
        super("", "https://www.curseforge.com");
        this.modidConsumer = modidConsumer;
    }

    @SneakyThrows
    @Override
    public void run(HttpClient client) {
        //https://www.curseforge.com/minecraft/mc-mods?page=1
        for (int i = 1; i < 1869; i++) {
            fetchPage(i, client, 0);
            Thread.sleep(1000L);
        }
    }

    private void fetchPage(int i, HttpClient client, int retries) {
        var payload = withKey("/minecraft/mc-mods?page=" + i)
                .GET().build();
        client.sendAsync(payload, HttpResponse.BodyHandlers.ofString())
                .thenApply(response -> {
                    var html = response.body();
                    if (response.statusCode() != 200) {
                        log.warn("Not 200 when fetching " + i + ", code: " + response.statusCode());
                        //System.out.println(html);
                        //   System.exit(0);
                        // delay and send
                        if (retries < 4) {
                            SCHEDULER.scheduleWithFixedDelay(() -> fetchPage(i, client, retries + 1), 0, 10, TimeUnit.SECONDS);
                        }
                        return null;
                    }
                    var matcher = MATCH_MOD_LNK.matcher(html);
                    while (matcher.find()) {
                        var lnk = matcher.group(1);
                        return lnk;
                    }
                    // nothing found?
                    log.warn("Cannot find anything matches the regex. retry...");
                    if (retries < 4) {
                        SCHEDULER.scheduleWithFixedDelay(() -> fetchPage(i, client, retries + 1), 0, 10, TimeUnit.SECONDS);
                    }
                    return null;
                })
                .thenAcceptAsync(modLnk -> fetchModId(modLnk, client, 0));
    }

    private void fetchModId(String modLnk, HttpClient client, int retries) {
        var payload = withKey(modLnk).GET().build();
        client.sendAsync(payload, HttpResponse.BodyHandlers.ofString())
                .thenAccept(resp -> {
                    if (resp.statusCode() != 200) {
                        log.warn("Not 200 when fetching " + modLnk);
                        // delay and send
                        if (retries < 4) {
                            SCHEDULER.scheduleWithFixedDelay(() -> fetchModId(modLnk, client, retries + 1), 0, 6, TimeUnit.SECONDS);
                        }
                    }
                    var body = resp.body();
                    var matcher = MODID_MATCH.matcher(body);
                    while (matcher.find()) {
                        var modid = Integer.parseInt(matcher.group(1));
                        if (modid <= 0) {
                            // invalid.
                            continue;
                        }
                        modidConsumer.accept(modid);
                        return;
                    }
                    if (retries < 4) {
                        SCHEDULER.scheduleWithFixedDelay(() -> fetchModId(modLnk, client, retries + 1), 0, 6, TimeUnit.SECONDS);
                    }
                });

    }
}
