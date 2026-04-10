const express = require('express');
const axios = require('axios');
const cors = require('cors');
const path = require('path');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('.'));

// Проксирование запросов к Python-серверу
const PYTHON_API_URL = process.env.PYTHON_API_URL || 'http://localhost:5000';

app.use('/api', async (req, res, next) => {
  try {
    const config = {
      method: req.method,
      url: `${PYTHON_API_URL}${req.originalUrl}`,
      headers: {
        ...req.headers,
        'Host': req.headers.host,
      },
      data: req.body,
    };

    const response = await axios(config);
    res.status(response.status).json(response.data);
  } catch (error) {
    if (error.response) {
      res.status(error.response.status).json(error.response.data);
    } else {
      res.status(500).json({ error: 'Internal server error' });
    }
  }
});

// Обработка статических файлов
app.get('*', (req, res) => {
  const filePath = path.join(__dirname, req.path);
  if (fs.existsSync(filePath) && !fs.lstatSync(filePath).isDirectory()) {
    res.sendFile(filePath);
  } else {
    res.sendFile(path.join(__dirname, 'web/pages/index.html'));
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
  console.log(`Proxying requests to Python API at ${PYTHON_API_URL}`);
});