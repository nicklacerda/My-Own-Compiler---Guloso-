
declare i32 @printf(i8*, ...)
@.fmt_int = private unnamed_addr constant [4 x i8] c"%d\0A\00", align 1

define i32 @main() {

    %x = alloca i32, align 4
    store i32 3, i32* %x, align 4
    %1 = load i32, i32* %x, align 4
    %2 = mul i32 %1, 5
    %y = alloca i32, align 4
    store i32 %2, i32* %y, align 4
    %3 = load i32, i32* %x, align 4
    %4 = load i32, i32* %y, align 4
    %5 = add i32 %3, %4
    %6 = load i32, i32* %x, align 4
    %7 = load i32, i32* %y, align 4
    %8 = sub i32 %6, %7
    %9 = sub i32 10, %8
    %10 = mul i32 %5, %9
    %z = alloca i32, align 4
    store i32 %10, i32* %z, align 4
    %11 = load i32, i32* %z, align 4
    %12 = getelementptr inbounds [4 x i8], [4 x i8]* @.fmt_int, i32 0, i32 0
    %13 = call i32 (i8*, ...) @printf(i8* %12, i32 %11)
    %14 = load i32, i32* %y, align 4
    %15 = icmp sgt i32 %14, 0
    br i1 %15, label %if_then_1, label %if_else_3
if_then_1:
    store i32 12, i32* %x, align 4
    br label %if_fim_2
if_else_3:
    %16 = load i32, i32* %y, align 4
    store i32 %16, i32* %x, align 4
    br label %if_fim_2
if_fim_2:
    %17 = load i32, i32* %x, align 4
    %18 = getelementptr inbounds [4 x i8], [4 x i8]* @.fmt_int, i32 0, i32 0
    %19 = call i32 (i8*, ...) @printf(i8* %18, i32 %17)

    ret i32 0
}
