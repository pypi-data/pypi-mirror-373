%  Copyright (c) 2018 IRT-AESE.
%  All rights reserved.
%
%  Contributors:
%     INITIAL AUTHORS - API and implementation and/or documentation
%         :author: Fran�ois Gallard
%
%     OTHER AUTHORS   - MACROSCOPIC CHANGES

% function y = dummy_test(x,y,z)
function [y, pid] = dummy_test_parallel(x)
y=x^2;
pid = feature("getpid");
pause(1);
end
