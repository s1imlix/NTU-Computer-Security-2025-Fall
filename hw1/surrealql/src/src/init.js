import { Surreal, Table } from "surrealdb";

const {
    SURREAL_HOST = "ws://surrealdb:8000/rpc",
    SURREAL_ROOT_USER = "root",
    SURREAL_ROOT_PASS = "root",
    SURREAL_NAMESPACE = "production",
    SURREAL_DATABASE = "main",
    SURREAL_USER = "viewer",
    SURREAL_PASS = "p4ssw0rd",
    SECRET_TABLE_NAME = "secret_table", // the name will be different on the remote server
    SECRET_COLUMN_NAME = "secret_column", // the name will be different on the remote server
    FLAG = "flag{th1s_1s_4_t3st_fl4g}", // of course, the flag will be different on the remote server
} = process.env;

let dbPromise = null;

async function initDB() {
    // Connect to the database as root
    const db = new Surreal();
    await db.connect(SURREAL_HOST);
    await db.ready;
    await db.signin({
        username: SURREAL_ROOT_USER,
        password: SURREAL_ROOT_PASS,
    });

    // Initialize the database
    await db.use({
        namespace: SURREAL_NAMESPACE,
        database: SURREAL_DATABASE,
    });
    const articleTable = new Table("article");
    const secretTable = new Table(SECRET_TABLE_NAME);
    await db.delete(articleTable);
    await db.delete(secretTable);
    await db.insert(secretTable, [
        {
            [SECRET_COLUMN_NAME]: FLAG,
        },
    ]);
    await db.insert(articleTable, [
        {
            title: "SurrealDB Basics",
            content: `Learn how to use SurrealDB with SurrealQL in your applications!

https://surrealdb.com/docs/surrealql`,
            created_at: new Date().toISOString(),
        },
        {
            title: "Hello World",
            content: "This is my first article.",
            created_at: new Date(
                new Date().getTime() - 1000 * 60 * 60,
            ).toISOString(),
        },
    ]);

    // Create a limited user that only has read access
    await db.query(`
        DEFINE USER IF NOT EXISTS ${SURREAL_USER}
        ON DATABASE
        PASSWORD "${SURREAL_PASS}"
        ROLES VIEWER;
    `);

    // Sign in as the limited user
    await db.invalidate();
    await db.signin({
        namespace: SURREAL_NAMESPACE,
        database: SURREAL_DATABASE,
        username: SURREAL_USER,
        password: SURREAL_PASS,
    });
    await db.use({
        namespace: SURREAL_NAMESPACE,
        database: SURREAL_DATABASE,
    });

    return db;
}

export function getDB() {
    if (!dbPromise) {
        dbPromise = initDB();
    }
    return dbPromise;
}
