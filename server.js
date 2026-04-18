const express = require('express');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

// Nombre del archivo donde se guardarán los usuarios
const DATA_FILE = path.join(__dirname, 'usuarios.json');

// Middlewares
app.use(express.json());
app.use(express.static('public')); // Para servir tu HTML

// 1. Obtener todos los usuarios
app.get('/api/usuarios', (req, res) => {
    if (!fs.existsSync(DATA_FILE)) {
        return res.json([]);
    }
    const data = fs.readFileSync(DATA_FILE, 'utf8');
    res.json(JSON.parse(data || '[]'));
});

// 2. Guardar/Actualizar la lista completa
app.post('/api/usuarios', (req, res) => {
    try {
        const usuarios = req.body;
        // Backup rápido antes de sobreescribir (Seguridad de datos)
        if (fs.existsSync(DATA_FILE)) {
            fs.copyFileSync(DATA_FILE, `${DATA_FILE}.bak`);
        }
        fs.writeFileSync(DATA_FILE, JSON.stringify(usuarios, null, 4));
        res.json({ success: true, message: 'Archivo actualizado correctamente' });
    } catch (error) {
        res.status(500).json({ success: false, message: 'Error al escribir el archivo' });
    }
});

app.listen(PORT, () => {
    console.log(`Servidor de gestión de usuarios en: http://localhost:${PORT}`);
});
