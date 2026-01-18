import express from "express";
import path from "path";
import { fileURLToPath } from "url";
import { getDB } from "./init.js";
import { RecordId } from "surrealdb";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const app = express();
app.set("view engine", "ejs");
app.set("views", path.join(__dirname, "/views"));
app.use(express.static(path.join(__dirname, "public")));

app.get("/", async (req, res) => {
    const sortOrder = req.query.sort || "DESC";
    try {
        const db = await getDB();
        const [articles] = await db
            .query(`SELECT * FROM article ORDER BY created_at ${sortOrder};`)
            .collect();
        res.render("index", { articles });
    } catch (err) {
        // console.log(err);
        res.status(500).send("Internal Server Error");
    }
});

app.get("/articles/:id", async (req, res) => {
    const id = req.params.id;
    try {
        const db = await getDB();
        const [article] = await db
            .query("SELECT * FROM ONLY $id", {
                id: new RecordId("article", id),
            })
            .collect();
        if (!article) {
            return res.status(404).send("Article not found");
        }
        res.render("article", { article });
    } catch (err) {
        res.status(500).send("Internal Server Error");
    }
});

app.listen(3000, () => {
    console.log("Server is running on http://localhost:3000");
});
