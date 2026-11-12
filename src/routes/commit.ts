import { Router } from "express";
import { Prisma } from "../../generated/prisma/client.js";
import { commitSchema } from "../schemas/commit.js";
import { commitStep } from "../services/commitStep.js";

export const commitRouter = Router();

commitRouter.post("/steps/commit", async (req, res) => {
  const parsed = commitSchema.safeParse(req.body);
  if (!parsed.success) {
    res.status(400).json({ error: "invalid_body", issues: parsed.error.issues });
    return;
  }
  try {
    res.status(201).json(await commitStep(parsed.data));
  } catch (e) {
    if (e instanceof Prisma.PrismaClientKnownRequestError) {
      if (e.code === "P2002") {
        res.status(409).json({ error: "tick_already_committed_on_branch" });
        return;
      }
      if (e.code === "P2003") {
        res.status(404).json({ error: "unknown_branch_or_agent" });
        return;
      }
    }
    throw e; // Express 5 forwards async errors to the handler below
  }
});
