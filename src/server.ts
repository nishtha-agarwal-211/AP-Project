import express, { type NextFunction, type Request, type Response } from "express";
import { commitRouter } from "./routes/commit.js";

const app = express();
app.use(express.json({ limit: "10mb" })); // embeddings + I/O bodies exceed the 100kb default
app.use("/api", commitRouter);

app.use((err: unknown, _req: Request, res: Response, _next: NextFunction) => {
  console.error(err);
  res.status(500).json({ error: "internal_error" });
});

app.listen(8000, () => console.log("API on http://localhost:8000")); // matches Config.api_base_url
