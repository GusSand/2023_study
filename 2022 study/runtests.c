#include <stddef.h>
#include <stdlib.h>
#include <setjmp.h>
#include <stdarg.h>
#include <stdio.h>
#include <unistd.h>
#include <string.h>
#include <stdint.h>
#include <signal.h>
#include "list.h"
#include "cmocka.h"

#ifdef _WIN32
// Compatibility with the Windows standard C library.
#define vsnprintf _vsnprintf
#endif /* _WIN32 */

static char big_buffer[1024];

int test_printf(const char *format, ...) CMOCKA_PRINTF_ATTRIBUTE(1, 2);

// A mock printf function that just gathers up the strings printed
// into a big buffer so that they can be checked later.
int test_printf(const char *format, ...) {
	int return_value;
    char temporary_buffer[256];
	va_list args;
	va_start(args, format);
	return_value = vsnprintf(temporary_buffer, sizeof(temporary_buffer),
	                         format, args);
    function_called();
    // Concatenate the temporary buffer to the big buffer.
    strcat(big_buffer, temporary_buffer);
	va_end(args);
	return return_value;
}

static void test_list_init(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_null(head);
}

static void test_list_add_item_at_pos(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item2", 2.0, 1, 2), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1.5", 1.5, 1, 2), EXIT_SUCCESS);
}

static void test_list_item_to_string(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    char str[100];
    assert_int_equal(list_item_to_string(head, str), EXIT_SUCCESS);
    // "quantity * item_name @ $price ea"
    assert_string_equal(str, "1 * item1 @ $1.00 ea");
}

static void test_list_print(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "banana", 1.0, 3, 1), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "orange", 2.0, 2, 2), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "apple", 3.0, 4, 3), EXIT_SUCCESS);
    expect_function_call_any(test_printf);
	assert_int_equal(list_print(head), EXIT_SUCCESS);
    char *expected_output = \
        "1: 3 * banana @ $1.00 ea\n" \
        "2: 2 * orange @ $2.00 ea\n" \
        "3: 4 * apple @ $3.00 ea\n";
    assert_string_equal(big_buffer, expected_output);
    memset(big_buffer, 0, sizeof(big_buffer));
}

static void test_list_update_item_at_pos(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    char *newname = "apple";
    assert_int_equal(list_update_item_at_pos(&head, newname, 3.0, 2, 1), EXIT_SUCCESS);
    assert_string_equal(head->item_name, newname);
    assert_float_equal(head->price, 3.0, 0.01);
    assert_int_equal(head->quantity, 2);
}

static void test_list_remove_item_at_pos(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    assert_int_equal(list_remove_item_at_pos(&head, 1), EXIT_SUCCESS);
    assert_null(head);
}

static void test_list_swap_item_positions(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item2", 2.0, 1, 2), EXIT_SUCCESS);
    assert_int_equal(list_swap_item_positions(&head, 1, 2), EXIT_SUCCESS);
    assert_string_equal(head->item_name, "item2");
    assert_string_equal(head->next->item_name, "item1");
}

static void test_list_find_highest_price_item_position(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item2", 1.0, 10, 2), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1.5", 5.0, 1, 3), EXIT_SUCCESS);
    int pos = 0;
    assert_int_equal(list_find_highest_price_item_position(head, &pos), EXIT_SUCCESS);
    assert_int_equal(pos, 3);
}

static void test_list_cost_sum(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item2", 1.0, 10, 2), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1.5", 5.0, 1, 3), EXIT_SUCCESS);
    float total = 0.0;
    assert_int_equal(list_cost_sum(head, &total), EXIT_SUCCESS);
    assert_float_equal(total, 16.0, 0.01);
}

static int getTempFilename(void **state) {
    char *filename = strdup("test.XXXXXX");
    // Silence compiler warning by using mkstemp
    int fd = mkstemp(filename);
    close(fd);
    *state = filename;
    return 0;
}

static int removeTempFile(void **state) {
    char *filename = *state;
    // We don't care if it fails
    remove(filename);
    free(filename);
    return 0;
}

static void test_list_save(void **state) {
    char *filename = *state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item2", 1.0, 10, 2), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1.5", 5.0, 1, 3), EXIT_SUCCESS);
    assert_int_equal(list_save(head, filename), EXIT_SUCCESS);
    FILE *fp = fopen(filename, "r");
    assert_non_null(fp);
    // Format: item_name,price,quantity\n
    char line[100];
    char *r = NULL;
    r = fgets(line, 100, fp);
    assert_non_null(r);
    assert_string_equal(line, "item1,1.00,1\n");
    r = fgets(line, 100, fp);
    assert_non_null(r);
    assert_string_equal(line, "item2,1.00,10\n");
    r = fgets(line, 100, fp);
    assert_non_null(r);
    assert_string_equal(line, "item1.5,5.00,1\n");
    r = fgets(line, 100, fp);
    assert_null(r);
    fclose(fp);
}


static void test_list_load(void **state) {
    (void) state;
    char *loadfile = "example_load_file.txt";
    node *head = NULL;
    assert_int_equal(list_load(&head, loadfile), EXIT_SUCCESS);
    // Expected list contents:
    // apple,0.80,2
    // banana,0.50,3
    // cheese,10.59,1
    assert_string_equal(head->item_name, "apple");
    assert_float_equal(head->price, 0.80, 0.01);
    assert_int_equal(head->quantity, 2);
    assert_string_equal(head->next->item_name, "banana");
    assert_float_equal(head->next->price, 0.50, 0.01);
    assert_int_equal(head->next->quantity, 3);
    assert_string_equal(head->next->next->item_name, "cheese");
    assert_float_equal(head->next->next->price, 10.59, 0.01);
    assert_int_equal(head->next->next->quantity, 1);
    assert_null(head->next->next->next);
}

static void test_list_deduplicate(void **state) {
    (void) state;
    node *head = NULL;
    assert_int_equal(list_init(&head), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 1, 1), EXIT_SUCCESS);
    assert_int_equal(list_add_item_at_pos(&head, "item1", 1.0, 10, 2), EXIT_SUCCESS);
    assert_int_equal(list_deduplicate(&head), EXIT_SUCCESS);
    assert_string_equal(head->item_name, "item1");
    assert_float_equal(head->price, 1.0, 0.01);
    assert_int_equal(head->quantity, 11);
    assert_null(head->next);
}

int main(void) {
	const struct CMUnitTest tests[] = {
		cmocka_unit_test(test_list_init),
        cmocka_unit_test(test_list_item_to_string),
        cmocka_unit_test(test_list_print),
        cmocka_unit_test(test_list_add_item_at_pos),
        cmocka_unit_test(test_list_update_item_at_pos),
        cmocka_unit_test(test_list_remove_item_at_pos),
        cmocka_unit_test(test_list_swap_item_positions),
        cmocka_unit_test(test_list_find_highest_price_item_position),
        cmocka_unit_test(test_list_cost_sum),
        // This test needs a temporary file to write to
        cmocka_unit_test_setup_teardown(test_list_save, getTempFilename, removeTempFile),
        cmocka_unit_test(test_list_load),
        cmocka_unit_test(test_list_deduplicate),
	};
	return cmocka_run_group_tests(tests, NULL, NULL);
}
