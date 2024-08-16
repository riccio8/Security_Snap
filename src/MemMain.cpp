#include "Offensive-defensive-tolls-/lib/MemVuln.hpp"
#include "Offensive-defensive-tolls-/lib/MemVuln.cpp"

using namespace std;

int main() {

    VulnerableVoid vul;
    MemType mem(1000, "Hello");


    vul.stack_overflow("ThisIsAVeryLongStringThatWillOverflowTheBufferInStackOverflowMethod");
    vul.heap_overflow("ThisIsALongStringThatWillCauseHeapOverflow");

    mem.MemLeak();
    mem.heapLeak();

    return 0;
}