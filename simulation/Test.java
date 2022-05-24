

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * @author: ming
 * @date: 2022/5/24 10:34
 */
public class Test {
    public static void main(String[] args) throws IOException {
        List<Integer> list = new ArrayList<>();
        List<List<Integer>> list2 = new ArrayList<>();
        list.add(1);
        list.add(2);
        list.add(3);
        list.add(4);
        list.add(5);
        list2.add(list);
        System.out.println(list2);
        List<Integer> list3 = new ArrayList<>();
        list3.add(9);
        list3.add(10);
        System.out.println(list3);
    }
}
