from psycopg import AsyncCursor, sql
from psycopg.rows import DictRow

from chancy.migrate import Migration, Migrator


class V1Migration(Migration):
    async def up(self, migrator: Migrator, cursor: AsyncCursor[DictRow]):
        # Create workflows table
        await cursor.execute(
            sql.SQL(
                """
                CREATE TABLE {workflows} (
                    id UUID PRIMARY KEY,
                    name TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            ).format(workflows=sql.Identifier(f"{migrator.prefix}workflows"))
        )

        # Create workflow_steps table
        await cursor.execute(
            sql.SQL(
                """
                CREATE TABLE {workflow_steps} (
                    id SERIAL PRIMARY KEY,
                    workflow_id UUID REFERENCES {workflows}(id)
                        ON DELETE CASCADE,
                    step_id TEXT NOT NULL,
                    job_data JSON NOT NULL,
                    dependencies JSON NOT NULL,
                    job_id UUID,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ DEFAULT NOW()
                )
                """
            ).format(
                workflow_steps=sql.Identifier(
                    f"{migrator.prefix}workflow_steps"
                ),
                workflows=sql.Identifier(f"{migrator.prefix}workflows"),
            )
        )

        # Create indexes
        await cursor.execute(
            sql.SQL(
                """
                CREATE INDEX {workflow_steps_workflow_id_idx} ON {workflow_steps} (workflow_id);
                CREATE INDEX {workflows_state_idx} ON {workflows} (state);
                CREATE UNIQUE INDEX {workflows_steps_unique_idx} ON {workflow_steps} (workflow_id, step_id);
                """
            ).format(
                workflow_steps=sql.Identifier(
                    f"{migrator.prefix}workflow_steps"
                ),
                workflows=sql.Identifier(f"{migrator.prefix}workflows"),
                workflow_steps_workflow_id_idx=sql.Identifier(
                    f"{migrator.prefix}workflow_steps_workflow_id_idx"
                ),
                workflow_steps_state_idx=sql.Identifier(
                    f"{migrator.prefix}workflow_steps_state_idx"
                ),
                workflows_state_idx=sql.Identifier(
                    f"{migrator.prefix}workflows_state_idx"
                ),
                workflows_steps_unique_idx=sql.Identifier(
                    f"{migrator.prefix}workflows_steps_unique_idx"
                ),
            )
        )

    async def down(self, migrator: Migrator, cursor: AsyncCursor[DictRow]):
        await cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {table}").format(
                table=sql.Identifier(f"{migrator.prefix}workflow_steps")
            )
        )

        await cursor.execute(
            sql.SQL("DROP TABLE IF EXISTS {table}").format(
                table=sql.Identifier(f"{migrator.prefix}workflows")
            )
        )
