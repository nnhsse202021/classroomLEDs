const express = require('express');
const fs = require('fs');
const path = require('path');

const router = express.Router();

const ledsFilePath = path.join(__dirname, './leds.json');

const getLED = async (req, res, next) => {
  try {
    const data = fs.readFileSync(ledsFilePath);
    const leds = JSON.parse(data);
    const led = leds.find(led => led.id === Number(req.params.id));
    if (!led) {
      const err = new Error('LED not found');
      err.status = 404;
      throw err;
    }
    res.json(led);
  } catch (e) {
    next(e);
  }
};

const updateLED = async (req, res, next) => {
  try {
    const data = fs.readFileSync(ledsFilePath);
    const leds = JSON.parse(data);
    const led = leds.find(led => led.id === Number(req.params.id));
    if (!led) {
      const err = new Error('LED not found');
      err.status = 404;
      throw err;
    }
    const newLEDData = {
      id: Number(req.params.id),
      color: req.body.color,
    };
    const newLEDs = leds.map(led => {
      if (led.id === Number(req.params.id)) {
        return newLEDData;
      } else {
        return led;
      }
    });
    fs.writeFileSync(ledsFilePath, JSON.stringify(newLEDs));
    res.status(200).json(newLEDData);
  } catch (e) {
    next(e);
  }
};

const getLEDs = async (req, res, next) => {
  try {
    const data = fs.readFileSync(ledsFilePath);
    const leds = JSON.parse(data);
    res.json(leds);
  } catch (e) {
    next(e);
  }
};



router
  .route('/leds/:id')
  .get(getLED)
  .put(updateLED);
  
router
  .route('/leds')
  .get(getLEDs);

module.exports = router;