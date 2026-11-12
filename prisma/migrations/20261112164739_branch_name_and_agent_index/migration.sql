-- AlterTable
ALTER TABLE "branches" ADD COLUMN     "name" TEXT;

-- CreateIndex
CREATE INDEX "execution_nodes_agent_id_idx" ON "execution_nodes"("agent_id");
