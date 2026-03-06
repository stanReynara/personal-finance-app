// server/utils/db.ts
import { drizzle } from 'drizzle-orm/node-postgres';
import pg from 'pg';
import * as schema from './schema';

const pool = new pg.Pool({
  connectionString: "postgres://stanley:your_password@localhost:5432/finance_db",
});

export const db = drizzle(pool, { schema });