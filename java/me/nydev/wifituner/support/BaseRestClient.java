package me.nydev.wifituner.support;

import android.content.Context;

import com.loopj.android.http.*;

import org.json.JSONObject;

import java.io.UnsupportedEncodingException;

import cz.msebera.android.httpclient.entity.StringEntity;
import me.nydev.wifituner.model.Auth;

public class BaseRestClient
{
    private static final String BASE_URL = "https://csci870.nydev.me/api/";

    private static AsyncHttpClient client = new AsyncHttpClient();

    public static void get(String url, RequestParams params, AsyncHttpResponseHandler responseHandler)
    {
        client.get(getAbsoluteUrl(url), params, responseHandler);
    }

    public static void post(String url, RequestParams params, AsyncHttpResponseHandler responseHandler)
    {
        client.post(getAbsoluteUrl(url), params, responseHandler);
    }

    public static void post(String url, JSONObject json, AsyncHttpResponseHandler responseHandler)
    {
        StringEntity entity = null;
        try {
            entity = new StringEntity(json.toString());
        } catch (UnsupportedEncodingException e) {
            e.printStackTrace();
        }
        client.post(null, getAbsoluteUrl(url), entity, "application/json", responseHandler);
    }

    private static String getAbsoluteUrl(String relativeUrl)
    {
        return BASE_URL + relativeUrl;
    }

    public static void auth(String username, String secret)
    {
        client.setBasicAuth(username, secret);
    }

    public static void auth(Auth a)
    {
        client.setBasicAuth(a.getUsername(), a.getSecret());
    }

    public static AsyncHttpClient getClient()
    {
        return client;
    }
}