CREATE EXTENSION IF NOT EXISTS vector;

-- CreateTable
CREATE TABLE "agents" (
    "agent_id" TEXT NOT NULL,
    "model_name" TEXT NOT NULL,
    "temperature" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "agents_pkey" PRIMARY KEY ("agent_id")
);

-- CreateTable
CREATE TABLE "state_snapshots" (
    "state_hash" CHAR(64) NOT NULL,
    "memory_blob_json" JSONB NOT NULL,
    "embedding_vector" vector(1536),
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "state_snapshots_pkey" PRIMARY KEY ("state_hash")
);

-- CreateTable
CREATE TABLE "execution_nodes" (
    "node_id" TEXT NOT NULL,
    "agent_id" TEXT NOT NULL,
    "state_hash" CHAR(64) NOT NULL,
    "lamport_tick" INTEGER NOT NULL,
    "prompt_input" TEXT NOT NULL,
    "llm_output" TEXT NOT NULL,
    "token_cost" DECIMAL(12,6) NOT NULL DEFAULT 0,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "execution_nodes_pkey" PRIMARY KEY ("node_id")
);

-- CreateIndex
CREATE INDEX "execution_nodes_state_hash_idx" ON "execution_nodes"("state_hash");

-- AddForeignKey
ALTER TABLE "execution_nodes" ADD CONSTRAINT "execution_nodes_agent_id_fkey" FOREIGN KEY ("agent_id") REFERENCES "agents"("agent_id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "execution_nodes" ADD CONSTRAINT "execution_nodes_state_hash_fkey" FOREIGN KEY ("state_hash") REFERENCES "state_snapshots"("state_hash") ON DELETE RESTRICT ON UPDATE CASCADE;
