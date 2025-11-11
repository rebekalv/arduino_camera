#include <sdk_config.h>
#include "nrfx.h"     
#include "nrfx_uarte.h"
#include "nrf_delay.h"
#include "nrf_log.h"
#include "nrf_log_ctrl.h"
#include "nrf_log_default_backends.h"

// UARTE
#define P1 32
#define UARTE_TX_PIN (P1+2)  // P1.02
#define UARTE_RX_PIN (P1+1)  // P1.01
#define UARTE_BAUDRATE NRF_UARTE_BAUDRATE_115200
#define RX_DATA_LENGTH 6
#define UARTE_TIMEOUT_MS 100

static const nrfx_uarte_t uarte1 = NRFX_UARTE_INSTANCE(1);
static uint8_t rx_buffer[RX_DATA_LENGTH];
static bool rx_done = false;
static bool tx_done = false;

void uarte1_event_handler(nrfx_uarte_event_t const * p_event, void * p_context)
{
    switch (p_event->type)
    {
        case NRFX_UARTE_EVT_TX_DONE:
            tx_done = true;
            NRF_LOG_INFO("Sent request");
            NRF_LOG_FLUSH();
            break;
        case NRFX_UARTE_EVT_RX_DONE:
            rx_done = true;
            break;
        default:
            break;
    }
}

void uarte1_init(void)
{
    nrfx_uarte_config_t  config = NRFX_UARTE_DEFAULT_CONFIG;
    config.pseltxd = UARTE_TX_PIN;
    config.pselrxd = UARTE_RX_PIN;
    config.baudrate = UARTE_BAUDRATE;
    config.hwfc = NRF_UARTE_HWFC_DISABLED;

    APP_ERROR_CHECK(nrfx_uarte_init(&uarte1, &config, uarte1_event_handler));

    NRF_LOG_INFO("UARTE1 initialized");
    NRF_LOG_FLUSH();
}

void uarte1_request_data(void)
{
    // Send request
    tx_done = false;
    uint8_t request_byte = 'r';
    APP_ERROR_CHECK(nrfx_uarte_tx(&uarte1, &request_byte, 1));
}

bool uarte1_receive_data(void)
{
    rx_done = false;
    APP_ERROR_CHECK(nrfx_uarte_rx(&uarte1, rx_buffer, RX_DATA_LENGTH));

    // Wait for RX with timeout
    uint32_t start_ms = 0;
    while (!rx_done)
    {
        __WFE(); // wait for events
        start_ms += 1; // approximate 1 ms per loop
        if (start_ms >= UARTE_TIMEOUT_MS)
        {
            NRF_LOG_WARNING("RX timeout, no response from camera");
            NRF_LOG_FLUSH();
            return false;
        }
    }
    return true;
}

int uarte1_get_line_estimate()
{
  uarte1_request_data();

  if(uarte1_receive_data())
  {
    int16_t x_start_mm = rx_buffer[0] | (rx_buffer[1] << 8);
    int16_t x_width_mm = rx_buffer[2] | (rx_buffer[3] << 8);
    int16_t distance_mm = rx_buffer[4] | (rx_buffer[5] << 8);

     NRF_LOG_INFO("x_start_mm: %d, x_width_mm: %d, distance_mm: %d", x_start_mm, x_width_mm, distance_mm);
     NRF_LOG_FLUSH();
  }
}

int main(void)
{
    APP_ERROR_CHECK(NRF_LOG_INIT(NULL));
    NRF_LOG_DEFAULT_BACKENDS_INIT();

    uarte1_init();

    while (true)
    {
    
        

        nrf_delay_ms(1000); // delay between requests
    }
}

