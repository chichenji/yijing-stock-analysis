import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { StitchProxy } from "@google/stitch-sdk";
import { ProxyAgent, setGlobalDispatcher } from "undici";

const apiKey = process.env.STITCH_API_KEY;
const proxyUrl = process.env.STITCH_PROXY_URL;

if (!apiKey) {
  throw new Error("STITCH_API_KEY is required for Stitch MCP proxy.");
}

if (proxyUrl) {
  setGlobalDispatcher(new ProxyAgent(proxyUrl));
}

const proxy = new StitchProxy({ apiKey });
const transport = new StdioServerTransport();

await proxy.start(transport);
