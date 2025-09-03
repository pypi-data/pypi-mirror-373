
(defsystem "defsystem" :class asdf::prebuilt-system
        :lib #P"SYS:LIBDEFSYSTEM.A"
        :depends-on NIL
        :components ((:compiled-file "defsystem" :pathname #P"SYS:DEFSYSTEM.FAS")))