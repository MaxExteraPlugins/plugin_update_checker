package com.maxexteraplugins.updatechecker;

import android.util.Log;

public class Main {
    private static final String TAG = "PluginUpdateChecker";

    public static void load() {
        try {
            Log.d(TAG, "Plugin Update Checker DEX loaded v1.8.0");
        } catch (Exception e) {
            Log.e(TAG, "Error loading Plugin Update Checker DEX", e);
        }
    }
}
