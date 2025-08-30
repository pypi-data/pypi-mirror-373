import { CapacitorConfig } from "@capacitor/cli";

const config: CapacitorConfig = {
    appId: "com.synerty.peek",
    appName: "peek",
    webDir: "dist",
    server: {
        androidScheme: "https",
    },
    ios: {
        preferredContentMode: "mobile",
        webContentsDebuggingEnabled: true,
    },
};

export default config;
